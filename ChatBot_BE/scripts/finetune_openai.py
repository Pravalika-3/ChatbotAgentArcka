import os
import glob
from openai import AzureOpenAI
from dotenv import load_dotenv
import time
import json
import requests
import logging
import argparse
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
logger.info("Environment variables loaded")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip('/')
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")

if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME]):
    logger.error("Missing required environment variables: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, or AZURE_OPENAI_DEPLOYMENT_NAME")
    raise ValueError("Missing required environment variables")

try:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    logger.info("AzureOpenAI client initialized")
except Exception as e:
    logger.error(f"Failed to initialize AzureOpenAI client: {str(e)}")
    raise

def list_available_deployments():
    logger.info("Listing available deployments")
    try:
        url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments?api-version={AZURE_OPENAI_API_VERSION}"
        headers = {
            "api-key": AZURE_OPENAI_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        deployments = response.json().get("data", [])
        deployment_ids = [deployment.get("id") for deployment in deployments]
        logger.info("Available deployments: %s", deployment_ids)
        return deployment_ids
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error listing deployments: %s - Response: %s", str(e), e.response.text if hasattr(e, 'response') else "No response")
        return []
    except requests.exceptions.RequestException as e:
        logger.error("Request error listing deployments: %s", str(e))
        return []
    except Exception as e:
        logger.error("Unexpected error listing deployments: %s", str(e))
        return []

def test_fine_tuning_endpoint():
    logger.info("Testing fine-tuning endpoint")
    try:
        jobs = client.fine_tuning.jobs.list(limit=5)
        job_ids = [job.id for job in jobs]
        logger.info("Recent fine-tuning jobs: %s", job_ids)
        return True
    except Exception as e:
        logger.error("Error accessing fine-tuning endpoint: %s", str(e))
        return False

def combine_jsonl_files(input_dir, combined_file):
    logger.info(f"Combining JSONL files from {input_dir} into {combined_file}")
    os.makedirs(os.path.dirname(combined_file), exist_ok=True)
    jsonl_files = glob.glob(os.path.join(input_dir, "*.jsonl"))
    if not jsonl_files:
        logger.error(f"No JSONL files found in {input_dir}")
        raise FileNotFoundError(f"No JSONL files found in {input_dir}")
    with open(combined_file, 'w', encoding='utf-8') as outfile:
        for jsonl_file in jsonl_files:
            logger.info(f"Adding {jsonl_file} to combined file")
            with open(jsonl_file, 'r', encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(line)

def verify_jsonl_file(jsonl_file):
    logger.info("Verifying JSONL file: %s", jsonl_file)
    try:
        if not os.path.exists(jsonl_file):
            raise FileNotFoundError(f"JSONL file not found: {jsonl_file}")
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            line_count = 0
            for i, line in enumerate(f, 1):
                data = json.loads(line.strip())
                if "messages" not in data:
                    raise ValueError(f"Invalid format in line {i}: 'messages' key missing. Expected chat completion format.")
                messages = data["messages"]
                if not all(msg.get("role") in ["system", "user", "assistant"] for msg in messages):
                    raise ValueError(f"Invalid format in line {i}: Invalid role in messages.")
                line_count = i
        logger.info(f"JSONL file format validated: {line_count} training examples found")
        return True
    except Exception as e:
        logger.error("Error verifying JSONL file: %s", str(e))
        return False

def upload_file(jsonl_file):
    logger.info("Uploading JSONL file: %s", jsonl_file)
    try:
        with open(jsonl_file, 'rb') as f:
            result = client.files.create(file=f, purpose="fine-tune")
        logger.info("File uploaded: ID=%s, Status=%s", result.id, result.status)
        for attempt in range(1, 31):
            file_status = client.files.retrieve(result.id)
            logger.info(f"File processing attempt {attempt}/30: status={file_status.status}")
            if file_status.status == "processed":
                logger.info("File processing completed")
                return result.id
            elif file_status.status == "error":
                raise Exception(f"File processing failed: {file_status.error}")
            time.sleep(10)
        raise Exception("File processing timed out")
    except Exception as e:
        logger.error("Error uploading file: %s", str(e))
        raise

def create_fine_tune_job(file_id, deployment_name):
    logger.info("Creating fine-tuning job for deployment: %s", deployment_name)
    try:
        result = client.fine_tuning.jobs.create(
            training_file=file_id,
            model=deployment_name
        )
        logger.info("Fine-tuning job created: ID=%s", result.id)
        with open("active_finetune_job.json", "w") as f:
            json.dump({"job_id": result.id, "start_time": datetime.now().isoformat()}, f)
        return result.id
    except Exception as e:
        logger.error("Error creating fine-tuning job: %s", str(e))
        raise

def monitor_fine_tune_job(job_id, timeout_hours=24):
    logger.info("Monitoring fine-tuning job: %s", job_id)
    start_time = datetime.now()
    timeout_time = start_time + timedelta(hours=timeout_hours)
    status_file = "finetune_status.txt"
    with open(status_file, "w") as f:
        f.write(f"Job ID: {job_id}\nStart time: {start_time.isoformat()}\nStatus: monitoring\n")
    retry_count = 0
    max_retries = 5
    while datetime.now() < timeout_time:
        try:
            job = client.fine_tuning.jobs.retrieve(job_id)
            status = job.status
            if hasattr(job, 'training_metrics') and job.training_metrics:
                metrics = job.training_metrics
                logger.info(f"Training metrics: {metrics}")
            with open(status_file, "a") as f:
                f.write(f"{datetime.now().isoformat()} - Status: {status}\n")
            elapsed = datetime.now() - start_time
            elapsed_hours = elapsed.total_seconds() / 3600
            logger.info(f"Fine-tuning job status: {status} (Running for {elapsed_hours:.2f} hours)")
            if status == "succeeded":
                fine_tuned_model = job.fine_tuned_model
                logger.info(f"Fine-tuning completed successfully after {elapsed_hours:.2f} hours")
                logger.info(f"Fine-tuned model ID: {fine_tuned_model}")
                return fine_tuned_model
            elif status == "failed":
                error_msg = job.error if hasattr(job, 'error') else "Unknown error"
                logger.error(f"Fine-tuning failed: {error_msg}")
                with open(status_file, "a") as f:
                    f.write(f"FAILED: {error_msg}\n")
                raise Exception(f"Fine-tuning failed: {error_msg}")
            elif status == "cancelled":
                logger.warning("Fine-tuning job was cancelled")
                with open(status_file, "a") as f:
                    f.write("CANCELLED\n")
                raise Exception("Fine-tuning job was cancelled")
            retry_count = 0
            if elapsed_hours < 1:
                time.sleep(60)
            elif elapsed_hours < 3:
                time.sleep(120)
            else:
                time.sleep(300)
        except Exception as e:
            retry_count += 1
            logger.error(f"Error monitoring fine-tuning job (attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count >= max_retries:
                logger.error("Too many consecutive errors. Please check the job manually.")
                with open(status_file, "a") as f:
                    f.write(f"MONITORING_ERROR: {str(e)}\n")
                raise Exception(f"Monitoring failed after {max_retries} retries: {str(e)}")
            time.sleep(120)
    logger.warning(f"Monitoring timed out after {timeout_hours} hours")
    with open(status_file, "a") as f:
        f.write(f"TIMEOUT: Exceeded {timeout_hours} hours\n")
    return f"TIMEOUT: Job {job_id} still running after {timeout_hours} hours. Check status manually."

def resume_monitoring():
    try:
        with open("active_finetune_job.json", "r") as f:
            data = json.load(f)
            job_id = data.get("job_id")
            start_time = data.get("start_time")
            if not job_id:
                return None
            logger.info(f"Resuming monitoring for job {job_id} (started at {start_time})")
            start_dt = datetime.fromisoformat(start_time)
            elapsed = datetime.now() - start_dt
            elapsed_hours = elapsed.total_seconds() / 3600
            remaining_hours = max(1, 24 - elapsed_hours)
            return monitor_fine_tune_job(job_id, timeout_hours=remaining_hours)
    except FileNotFoundError:
        logger.info("No active fine-tuning job found to resume")
        return None
    except Exception as e:
        logger.error(f"Error resuming monitoring: {str(e)}")
        return None

def finetune_azure_openai(input_dir="data/messages", combined_file="data/combined_finetune_messages.jsonl", deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME, output_file="fine_tuned_model.json", resume=False):
    logger.info("Starting fine-tuning process for deployment: %s", deployment_name)
    if resume:
        logger.info("Attempting to resume monitoring previous job")
        result = resume_monitoring()
        if result:
            if isinstance(result, str) and result.startswith("TIMEOUT"):
                logger.warning(result)
                return None
            else:
                with open(output_file, 'w') as f:
                    json.dump({"fine_tuned_model": result}, f)
                logger.info("Fine-tuned model ID saved to %s", output_file)
                return result
    try:
        if not test_fine_tuning_endpoint():
            logger.warning("Fine-tuning endpoint may not be available in this resource or region. Consider checking region or contacting Azure support.")
        combine_jsonl_files(input_dir, combined_file)
        if not verify_jsonl_file(combined_file):
            raise ValueError(f"Invalid or inaccessible JSONL file: {combined_file}")
        available_deployments = list_available_deployments()
        if deployment_name not in available_deployments:
            logger.warning("Deployment %s not found in available deployments: %s", deployment_name, available_deployments)
            logger.info("Proceeding with fine-tuning anyway, as deployment may still be valid")
        file_id = upload_file(combined_file)
        job_id = create_fine_tune_job(file_id, deployment_name)
        fine_tuned_model = monitor_fine_tune_job(job_id)
        if isinstance(fine_tuned_model, str) and fine_tuned_model.startswith("TIMEOUT"):
            logger.warning(fine_tuned_model)
            return None
        with open(output_file, 'w') as f:
            json.dump({"fine_tuned_model": fine_tuned_model}, f)
        logger.info("Fine-tuned model ID saved to %s", output_file)
        return fine_tuned_model
    except Exception as e:
        logger.error("Fine-tuning process failed: %s", str(e))
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune Azure OpenAI model")
    parser.add_argument("--input-dir", default="data/messages", help="Directory containing message JSONL files")
    parser.add_argument("--combined-file", default="data/combined_finetune_messages.jsonl", help="Path to the combined JSONL file")
    parser.add_argument("--model", default=AZURE_OPENAI_DEPLOYMENT_NAME, help="Deployment name to fine-tune")
    parser.add_argument("--output", default="fine_tuned_model.json", help="Output file to save the fine-tuned model ID")
    parser.add_argument("--resume", action="store_true", help="Resume monitoring an existing fine-tuning job")
    parser.add_argument("--timeout", type=int, default=24, help="Timeout in hours for monitoring")
    
    args = parser.parse_args()
    
    logger.info(f"Using deployment name: {args.model}")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Combined file: {args.combined_file}")
    logger.info(f"Output file: {args.output}")
    logger.info(f"Resume monitoring: {args.resume}")
    
    finetune_azure_openai(args.input_dir, args.combined_file, args.model, args.output, args.resume)