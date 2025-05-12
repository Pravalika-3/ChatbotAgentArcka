import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_jsonl_file(jsonl_file):
    logger.info("Verifying JSONL file: %s", jsonl_file)
    try:
        if not os.path.exists(jsonl_file):
            raise FileNotFoundError(f"JSONL file not found: {jsonl_file}")
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                data = json.loads(line.strip())
                if "messages" not in data:
                    raise ValueError(f"Invalid format in line {i}: 'messages' key missing.")
                messages = data["messages"]
                if not all(msg.get("role") in ["system", "user", "assistant"] for msg in messages):
                    raise ValueError(f"Invalid format in line {i}: Invalid role in messages.")
        logger.info("JSONL file format validated")
        return True
    except Exception as e:
        logger.error("Error verifying JSONL file: %s", str(e))
        return False

jsonl_file = "rbac_finetune.jsonl"
verify_jsonl_file(jsonl_file)