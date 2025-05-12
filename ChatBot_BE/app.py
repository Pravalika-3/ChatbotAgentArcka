from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import msal
import pyodbc
import platform
import json
import requests
import re
from typing import List, Dict, Optional
from resume_manager.fetcher import SharePointFetcher
from resume_manager.parser import ResumeParser
import chromadb
from chromadb.api.types import EmbeddingFunction
import hashlib
import logging
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('.env', override=True)
logger.info(f".env file path: {os.path.abspath('.env')}")

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")
EMBEDDING_ENDPOINT = os.getenv("EMBEDDING_ENDPOINT")
EMBEDDING_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEFAULT_MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

SHAREPOINT_TENANT_ID = os.getenv("SHAREPOINT_TENANT_ID")
SHAREPOINT_CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID")
SHAREPOINT_CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET")
SHAREPOINT_DOMAIN = os.getenv("SHAREPOINT_DOMAIN")
SHAREPOINT_SITE_NAME = os.getenv("SHAREPOINT_SITE_NAME")
SHAREPOINT_FOLDER_PATH = os.getenv("SHAREPOINT_FOLDER_PATH")

logger.info("Environment variables loaded:")
logger.info(f"SQL_SERVER: {SQL_SERVER}")
logger.info(f"SQL_DATABASE: {SQL_DATABASE}")
logger.info(f"SQL_USERNAME: {'Set' if SQL_USERNAME else 'Not set'}")
logger.info(f"TENANT_ID: {'Set' if TENANT_ID else 'Not set'}")
logger.info(f"CLIENT_ID: {'Set' if CLIENT_ID else 'Not set'}")
logger.info(f"AZURE_OPENAI_API_KEY: {'Set' if AZURE_OPENAI_API_KEY else 'Not set'}")
logger.info(f"AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
logger.info(f"AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION}")
logger.info(f"DEFAULT_MODEL: {DEFAULT_MODEL}")
logger.info(f"EMBEDDING_API_KEY: {'Set' if EMBEDDING_API_KEY else 'Not set'}")
logger.info(f"EMBEDDING_ENDPOINT: {EMBEDDING_ENDPOINT}")
logger.info(f"EMBEDDING_API_VERSION: {EMBEDDING_API_VERSION}")
logger.info(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
logger.info(f"SHAREPOINT_TENANT_ID: {'Set' if SHAREPOINT_TENANT_ID else 'Not set'}")
logger.info(f"SHAREPOINT_CLIENT_ID: {'Set' if SHAREPOINT_CLIENT_ID else 'Not set'}")
logger.info(f"SHAREPOINT_CLIENT_SECRET: {'Set' if SHAREPOINT_CLIENT_SECRET else 'Not set'}")
logger.info(f"SHAREPOINT_DOMAIN: {SHAREPOINT_DOMAIN}")
logger.info(f"SHAREPOINT_SITE_NAME: {SHAREPOINT_SITE_NAME}")
logger.info(f"SHAREPOINT_FOLDER_PATH: {SHAREPOINT_FOLDER_PATH}")

required_vars = [
    "EMBEDDING_API_KEY",
    "EMBEDDING_ENDPOINT",
    "SHAREPOINT_TENANT_ID",
    "SHAREPOINT_CLIENT_ID",
    "SHAREPOINT_CLIENT_SECRET",
    "AZURE_OPENAI_EMBEDDING_MODEL",
    "TENANT_ID",
    "CLIENT_ID"
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

def validate_azure_openai_config(api_key: str, endpoint: str, api_version: str, model: str) -> tuple[bool, str]:
    """
    Validate Azure OpenAI API key and endpoint by checking format and making a test request.
    Returns (is_valid, error_message).
    """
    if not api_key or not re.match(r'^[0-9a-fA-F]{32}$', api_key):
        error_msg = "Invalid Azure OpenAI API key format. It should be a 32-character hexadecimal string."
        logger.error(error_msg)
        return False, error_msg

    endpoint_pattern = r'^https://[a-z0-9-]+\.openai\.azure\.com/?$'
    if not endpoint or not re.match(endpoint_pattern, endpoint):
        error_msg = f"Invalid Azure OpenAI endpoint format: {endpoint}. Expected format: https://<resource-name>.openai.azure.com/."
        logger.error(error_msg)
        return False, error_msg

    test_url = f"{endpoint.rstrip('/')}/openai/deployments/{model}/embeddings?api-version={api_version}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {"input": "Test embedding"}
    try:
        response = requests.post(test_url, headers=headers, json=body, timeout=10)
        if response.status_code == 200:
            logger.info(f"Azure OpenAI endpoint validated successfully: {endpoint}")
            return True, ""
        elif response.status_code == 401:
            error_msg = "Authentication failed: Invalid Azure OpenAI API key."
            logger.error(error_msg)
            return False, error_msg
        elif response.status_code == 404:
            error_msg = f"Endpoint or model not found: {endpoint}/{model}."
            logger.error(error_msg)
            return False, error_msg
        else:
            error_msg = f"Failed to access Azure OpenAI endpoint: {endpoint}. Status code: {response.status_code}, Response: {response.text}."
            logger.error(error_msg)
            return False, error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Error connecting to Azure OpenAI endpoint {endpoint}: {str(e)}."
        logger.error(error_msg)
        return False, error_msg

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception)
)
def initialize_azure_openai_client(api_key: str, endpoint: str, api_version: str) -> AzureOpenAI:
    """Initialize Azure OpenAI client with retry logic."""
    return AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )

embedding_client = None
is_embedding_enabled = False
embedding_error = None
try:
    is_valid, validation_error = validate_azure_openai_config(
        EMBEDDING_API_KEY,
        EMBEDDING_ENDPOINT,
        EMBEDDING_API_VERSION,
        EMBEDDING_MODEL
    )
    if not is_valid:
        raise ValueError(validation_error)

    embedding_client = initialize_azure_openai_client(
        EMBEDDING_API_KEY,
        EMBEDDING_ENDPOINT,
        EMBEDDING_API_VERSION
    )
    logger.info("AzureOpenAI embedding client initialized successfully")
    is_embedding_enabled = True
except Exception as e:
    embedding_error = str(e)
    logger.error(f"Failed to initialize AzureOpenAI embedding client: {embedding_error}")
    embedding_client = None
    is_embedding_enabled = False

general_client = None
is_general_enabled = False
general_error = None
try:
    is_valid, validation_error = validate_azure_openai_config(
        AZURE_OPENAI_API_KEY,
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_API_VERSION,
        DEFAULT_MODEL
    )
    if is_valid:
        general_client = initialize_azure_openai_client(
            AZURE_OPENAI_API_KEY,
            AZURE_OPENAI_ENDPOINT,
            AZURE_OPENAI_API_VERSION
        )
        logger.info("AzureOpenAI general client initialized successfully")
        is_general_enabled = True
    else:
        raise ValueError(validation_error)
except Exception as e:
    general_error = str(e)
    logger.error(f"Failed to initialize AzureOpenAI general client: {general_error}")
    general_client = None
    is_general_enabled = False

app = FastAPI()
router = APIRouter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AzureOpenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, endpoint: str, model: str, api_version: str):
        if not is_embedding_enabled:
            raise ValueError("Embedding functionality is disabled due to Azure OpenAI client initialization failure.")
        self.client = embedding_client
        self.model = model

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(Exception)
    )
    def __call__(self, input: List[str]) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=input
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated embeddings for {len(input)} inputs")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

class VectorDBManager:
    def __init__(self, db_path="vector_db", collection_name="resumes"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = None
        self.collection = None
        if is_embedding_enabled:
            try:
                self.embedding_function = AzureOpenAIEmbeddingFunction(
                    api_key=EMBEDDING_API_KEY,
                    endpoint=EMBEDDING_ENDPOINT,
                    model=EMBEDDING_MODEL,
                    api_version=EMBEDDING_API_VERSION
                )
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"VectorDBManager initialized with collection: {collection_name}")
            except Exception as e:
                logger.error(f"Failed to initialize VectorDBManager: {str(e)}")
                self.embedding_function = None
                self.collection = None
        else:
            logger.warning("VectorDBManager initialized without embedding functionality.")
        self.max_tokens = 8192

    def compute_file_hash(self, content: str):
        hasher = hashlib.sha256()
        hasher.update(content.encode('utf-8'))
        return hasher.hexdigest()

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def embed_resume(self, file_id: str, content: str, metadata: Dict):
        if not self.collection or not is_embedding_enabled:
            logger.warning(f"Skipping embedding for {file_id}: Embedding functionality is disabled.")
            return False
        try:
            token_count = self.estimate_tokens(content)
            if token_count > self.max_tokens:
                logger.warning(f"Content for {file_id} exceeds {self.max_tokens} tokens ({token_count}). Truncating.")
                content = content[:self.max_tokens * 4]
                token_count = self.estimate_tokens(content)
                logger.info(f"Truncated content to {token_count} tokens.")

            file_hash = self.compute_file_hash(content)
            existing = self.collection.get(ids=[file_id])
            if existing['ids'] and existing['metadatas'][0].get('file_hash') == file_hash:
                logger.info(f"Skipping unchanged resume: {metadata['file_name']}")
                return False

            self.collection.upsert(
                documents=[content],
                metadatas=[{**metadata, 'file_hash': file_hash}],
                ids=[file_id]
            )
            logger.info(f"Embedded resume: {metadata['file_name']} ({token_count} tokens)")
            return True
        except Exception as e:
            logger.error(f"Error embedding resume {file_id}: {str(e)}")
            return False

    def embed_resumes(self, parsed_resumes: Dict[str, str], metadata_manager):
        if not is_embedding_enabled:
            logger.warning("Embedding skipped: Azure OpenAI embedding client is not initialized.")
            return 0
        embedded_count = 0
        for file_id, content in parsed_resumes.items():
            file_metadata = metadata_manager.metadata.get(file_id)
            if not file_metadata:
                logger.warning(f"No metadata found for file ID: {file_id}")
                continue
            file_metadata['file_id'] = file_id
            logger.info(f"Metadata for {file_id}: {file_metadata}")
            if self.embed_resume(file_id, content, file_metadata):
                embedded_count += 1
        logger.info(f"Total resumes embedded: {embedded_count}")
        return embedded_count

    def search_resumes(self, query: str, n_results: int = 5):
        if not self.collection or not is_embedding_enabled:
            error_detail = f"Resume search is unavailable. Embedding client not initialized. Error details: {embedding_error}"
            logger.error(error_detail)
            raise HTTPException(status_code=503, detail=error_detail)
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            logger.info(f"Resume search for query '{query}' returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error searching resumes: {str(e)}")
            raise

@app.on_event("startup")
async def startup_event():
    logger.info("App startup: Initializing SharePoint Fetch + Resume Parsing + Embedding...")
    try:
        authority = f"https://login.microsoftonline.com/{SHAREPOINT_TENANT_ID}"
        app_msal = msal.ConfidentialClientApplication(
            client_id=SHAREPOINT_CLIENT_ID,
            authority=authority,
            client_credential=SHAREPOINT_CLIENT_SECRET
        )
        token_result = app_msal.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in token_result:
            raise Exception(f"Token fetch failed: {token_result.get('error_description', 'Unknown error')}")
        access_token = token_result["access_token"]
        logger.info("SharePoint Graph token acquired.")

        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        site_lookup_url = f"https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_DOMAIN}:/sites/{SHAREPOINT_SITE_NAME}"
        site_response = requests.get(site_lookup_url, headers=headers)
        site_response.raise_for_status()
        site_info = site_response.json()
        site_id = site_info["id"]
        logger.info(f"Resolved Site ID: {site_id}")

        fetcher = SharePointFetcher(
            access_token=access_token,
            site_id=site_id,
            folder_path=SHAREPOINT_FOLDER_PATH,
            download_dir="resumes"
        )
        fetcher.fetch_and_update()
        logger.info("Resumes fetched and metadata updated.")

        parser = ResumeParser(resume_dir="resumes")
        metadata_manager = fetcher.metadata_manager
        new_or_updated_files = list(metadata_manager.metadata.keys())
        valid_extensions = ('.pdf', '.docx')
        resume_files = [
            file_id for file_id in new_or_updated_files
            if file_id.lower().endswith(valid_extensions) and
            not any(keyword in file_id.lower() for keyword in ['website', 'policy', 'agentmodel', 'agentzero'])
        ]
        logger.info(f"Found {len(resume_files)} new/updated resumes to parse (filtered).")
        parsed_resumes = {}
        for file_id in resume_files:
            file_metadata = metadata_manager.metadata.get(file_id)
            if not file_metadata:
                logger.warning(f"No metadata found for file ID: {file_id}")
                continue
            if 'file_name' not in file_metadata:
                file_metadata['file_name'] = file_id
                logger.info(f"Set file_name to file_id for {file_id}")
            file_name = file_metadata['file_name']
            try:
                logger.info(f"Parsing resume: {file_name}")
                parsed_data = parser.parse_resume(file_id)
                if isinstance(parsed_data, str) and parsed_data.strip():
                    parsed_resumes[file_id] = parsed_data
                else:
                    logger.warning(f"Invalid or empty parsed data for {file_id}")
            except Exception as e:
                logger.warning(f"Failed to parse resume for file ID {file_id} (name: {file_name}): {str(e)}")
                continue
        logger.info(f"Successfully parsed {len(parsed_resumes)} resumes.")

        if is_embedding_enabled:
            vector_db = VectorDBManager()
            embedded_count = vector_db.embed_resumes(parsed_resumes, metadata_manager)
            logger.info(f"Embedded {embedded_count} new or updated resumes into vector database.")
        else:
            logger.warning("Skipping resume embedding due to embedding client initialization failure.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

class LoginRequest(BaseModel):
    email: str

class ChatRequest(BaseModel):
    message: str
    userEmail: str
    userRoles: List[Dict]
    accessibleTables: List[str]
    conversation_state: Optional[Dict] = None
    format: str = "text"

class MessageClassificationRequest(BaseModel):
    message: str
    accessibleTables: List[str]
    userEmail: str
    userRoles: List[Dict]

class ResumeSearchRequest(BaseModel):
    query: str
    userEmail: str
    userRoles: List[Dict]
    n_results: int = 5

def get_access_token():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    msal_app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=authority)
    accounts = msal_app.get_accounts(username=SQL_USERNAME)
    if accounts:
        result = msal_app.acquire_token_silent(scopes=["https://database.windows.net/.default"], account=accounts[0])
        if result:
            return result["access_token"]
    result = msal_app.acquire_token_interactive(scopes=["https://database.windows.net/.default"])
    if "access_token" in result:
        return result["access_token"]
    raise Exception(f"Failed to acquire token: {result.get('error')} - {result.get('error_description')}")

def establish_connection():
    driver = "{ODBC Driver 17 for SQL Server}" if platform.system() == 'Windows' else "{ODBC Driver 18 for SQL Server}"
    connection_string = f"Driver={driver};Server={SQL_SERVER};Database={SQL_DATABASE};Authentication=ActiveDirectoryInteractive;UID={SQL_USERNAME};"
    try:
        conn = pyodbc.connect(connection_string)
        return conn, None
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def get_user_role(email):
    conn, error = establish_connection()
    if error:
        raise HTTPException(status_code=500, detail=error)
    cursor = conn.cursor()
    query = """
    SELECT r.RoleID, r.RoleName 
    FROM [dbo].[UserRoleMapping] urm
    JOIN [dbo].[Roles] r ON urm.RoleID = r.RoleID
    WHERE urm.UserEmail = ? AND urm.IsActive = 1
    """
    cursor.execute(query, (email,))
    roles = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    if not roles:
        raise HTTPException(status_code=401, detail="No active roles found for this email")
    return roles

def get_all_database_objects():
    conn, error = establish_connection()
    if error:
        raise HTTPException(status_code=500, detail=error)
    cursor = conn.cursor()
    tables_query = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'dbo' AND TABLE_TYPE = 'BASE TABLE'
    """
    cursor.execute(tables_query)
    tables = [row[0] for row in cursor.fetchall()]
    views_query = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.VIEWS 
    WHERE TABLE_SCHEMA = 'dbo'
    """
    cursor.execute(views_query)
    views = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables + views

def get_role_definitions():
    conn, error = establish_connection()
    if error:
        raise HTTPException(status_code=500, detail=error)
    cursor = conn.cursor()
    check_query = """
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'RoleTableMapping'
    """
    cursor.execute(check_query)
    table_exists = cursor.fetchone()[0] > 0
    if table_exists:
        roles_query = """
        SELECT r.RoleName, rtm.TableName
        FROM [dbo].[RoleTableMapping] rtm
        JOIN [dbo].[Roles] r ON rtm.RoleID = r.RoleID
        WHERE rtm.IsActive = 1
        """
        cursor.execute(roles_query)
        role_mappings = cursor.fetchall()
        role_definitions = {}
        for role_name, table_name in role_mappings:
            if role_name not in role_definitions:
                role_definitions[role_name] = []
            role_definitions[role_name].append(table_name)
        conn.close()
        return role_definitions
    else:
        conn.close()
        return {
            "Admin": [],
            "Recruiter": ["Sourcing", "Candidate", "Education", "PreferredLocation", "NoticePeriod"],
            "Requestor": ["Request", "Requisition", "Vacancy", "Position", "WorkLocation", "Employee"],
            "Interviewer": ["Feedback", "Interview", "Interviewer"]
        }

def define_table_access_by_role(role_name, all_objects):
    role_definitions = get_role_definitions()
    if role_name == "Admin":
        return all_objects
    patterns = role_definitions.get(role_name, [])
    accessible = []
    if not patterns:
        patterns = [role_name]
    for obj in all_objects:
        if any(pattern.lower() in obj.lower() for pattern in patterns):
            accessible.append(obj)
    return accessible

def get_table_schema(table_name):
    conn, error = establish_connection()
    if error:
        raise HTTPException(status_code=500, detail=error)
    cursor = conn.cursor()
    table_check_query = """
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?
    """
    cursor.execute(table_check_query, (table_name,))
    table_exists = cursor.fetchone()[0] > 0
    if table_exists:
        schema_query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        cursor.execute(schema_query)
        columns = cursor.fetchall()
        schema = f"CREATE TABLE [dbo].[{table_name}](\n"
        for i, col in enumerate(columns):
            column_name, data_type, max_length, is_nullable, default_value = col
            data_type_str = f"{data_type}({max_length})" if max_length and max_length != -1 and data_type in ('char', 'varchar', 'nchar', 'nvarchar') else data_type
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default = f" DEFAULT {default_value}" if default_value else ""
            comma = "" if i == len(columns) - 1 else ","
            schema += f"    [{column_name}] [{data_type_str}] {nullable}{default}{comma}\n"
        schema += ")"
        conn.close()
        return schema
    else:
        view_check_query = """
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.VIEWS 
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?
        """
        cursor.execute(view_check_query, (table_name,))
        view_exists = cursor.fetchone()[0] > 0
        if view_exists:
            view_def_query = f"""
            SELECT VIEW_DEFINITION
            FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{table_name}'
            """
            cursor.execute(view_def_query)
            view_def = cursor.fetchone()[0]
            schema = f"CREATE VIEW [dbo].[{table_name}] AS\n{view_def}"
            conn.close()
            return schema
        conn.close()
        raise HTTPException(status_code=404, detail=f"The {table_name} table/view does not exist")

def get_completion_from_azure_openai(model_id: str, prompt: str, temperature: float = 0.5, max_tokens: int = 1000):
    if not is_general_enabled or general_client is None:
        return None, f"Azure OpenAI general client not initialized. Error: {general_error}"
    try:
        logger.info(f"Sending request to Azure OpenAI: Model={model_id}, Prompt (first 100 chars)={prompt[:100]}...")
        response = general_client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in the Recruitment Management System's RBAC and resume search."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        response_content = response.choices[0].message.content
        logger.info(f"Response received from {model_id} (first 100 chars): {response_content[:100]}...")
        return response_content, None
    except Exception as e:
        error_message = str(e).lower()
        if "authentication" in error_message or "api key" in error_message:
            detail = "Authentication error: Invalid or missing Azure OpenAI API key."
        elif "resource" in error_message or "endpoint" in error_message:
            detail = f"Resource error: Invalid endpoint URL ({AZURE_OPENAI_ENDPOINT})."
        elif "deployment" in error_message or "model" in error_message:
            detail = f"Deployment error: Model '{model_id}' not found or not deployed."
        elif "rate limit" in error_message:
            detail = "Rate limit exceeded: Please try again later."
        elif "timed out" in error_message:
            detail = "Request timed out: Check network connectivity to Azure OpenAI."
        elif "quota" in error_message or "credits" in error_message:
            detail = "Quota exceeded: Azure OpenAI credits for gpt-35-turbo are exhausted."
        else:
            detail = f"Unexpected error: {str(e)}"
        logger.error(f"Error in Azure OpenAI request for model {model_id}: {detail}")
        return None, detail

def get_nl2sql_response(question, table_name, schema, user_role=None):
    role_context = f"\nNote that this query is being made by a user with {user_role} role. " if user_role else ""
    if user_role and user_role != "Admin":
        if any(op in question.lower() for op in ["delete", "drop", "truncate", "update", "insert", "create"]):
            raise HTTPException(status_code=403, detail="You don't have permission to perform data modification operations")
    prompt = f"""Given the following SQL Server database schema:
{schema}

Convert this question into a SQL query to run against the {table_name} table/view:
{question}{role_context}

Return only the SQL query without any explanation or additional text.
"""
    sql_response, error = get_completion_from_azure_openai(DEFAULT_MODEL, prompt, temperature=0.1, max_tokens=500)
    if error:
        raise HTTPException(status_code=500, detail=error)
    
    if "```sql" in sql_response:
        sql_match = re.search(r'```sql(.+?)```', sql_response, re.DOTALL)
        if sql_match:
            sql_response = sql_match.group(1).strip()
    elif "```" in sql_response:
        sql_match = re.search(r'```(.+?)```', sql_response, re.DOTALL)
        if sql_match:
            sql_response = sql_match.group(1).strip()
    if "LIMIT" in sql_response:
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_response, re.IGNORECASE)
        if limit_match:
            limit_num = limit_match.group(1)
            sql_response = re.sub(r'LIMIT\s+\d+', '', sql_response, flags=re.IGNORECASE)
            sql_response = sql_response.replace("SELECT", f"SELECT TOP {limit_num}", 1)
    return sql_response

def execute_sql_query(sql_query):
    conn, error = establish_connection()
    if error:
        raise HTTPException(status_code=500, detail=error)
    cursor = conn.cursor()
    logger.info(f"Executing SQL query: {sql_query}")
    try:
        cursor.execute(sql_query)
        columns = [column[0] for column in cursor.description] if cursor.description else []
        results = []
        if columns:
            rows = cursor.fetchall()
            for row in rows:
                result_row = {}
                for i, value in enumerate(row):
                    if isinstance(value, (bytes, bytearray)):
                        value = "<binary data>"
                    elif hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    result_row[columns[i]] = value
                results.append(result_row)
        conn.close()
        logger.info(f"Query returned {len(results)} results")
        return results
    except Exception as e:
        conn.close()
        error_message = f"SQL query execution error: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)

def convert_results_to_natural_language(results, question, table_name):
    if not results:
        return "I didn't find any data matching your query."
    results_json = json.dumps(results, indent=2)
    prompt = f"""Here are the results of a query against the {table_name} table:
```json
{results_json}
```

The original question was: "{question}"

Please convert these SQL query results into a natural language response that directly answers the question.
Make your response conversational and friendly. Focus on the key information and insights. 
Only mention specific numbers if they're significant to the answer.
DO NOT mention SQL, queries, or tables in your response.
"""
    response, error = get_completion_from_azure_openai(DEFAULT_MODEL, prompt, temperature=0.5, max_tokens=1000)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return response

@app.post("/api/login")
async def login(request: LoginRequest):
    try:
        roles = get_user_role(request.email)
        all_database_objects = get_all_database_objects()
        accessible_objects = []
        for role in roles:
            role_objects = define_table_access_by_role(role["name"], all_database_objects)
            accessible_objects.extend(role_objects)
        accessible_objects = list(set(accessible_objects))
        logger.info(f"User {request.email} logged in with roles: {[role['name'] for role in roles]}")
        return {
            "success": True,
            "email": request.email,
            "roles": roles,
            "accessibleTables": accessible_objects
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/classify-message")
async def classify_message(request: MessageClassificationRequest):
    try:
        logger.info(f"Classifying message: {request.message[:50]}...")
        tables_list = ", ".join(request.accessibleTables[:10])
        additional_tables = f" and {len(request.accessibleTables) - 10} more" if len(request.accessibleTables) > 10 else ""
        prompt = f"""
You are an AI assistant that helps classify user questions.

Classify the following user message into exactly one of these categories:
- "conversational": greetings, jokes, casual questions about yourself or chit-chat.
- "database_query": asking about structured data from database tables or business-related information.
- "resume_query": asking about people, candidates, resumes, individual names, skills, work experience, job roles, certifications, technologies known, years of experience.

Message: "{request.message}"

Available database tables: {tables_list}{additional_tables}

Return only one word: "conversational", "database_query", or "resume_query".
"""
        response_text, error = get_completion_from_azure_openai(
            DEFAULT_MODEL,
            prompt,
            temperature=0.1,
            max_tokens=20
        )
        if error:
            if "Quota exceeded" in error:
                logger.warning("Falling back to conversational classification due to quota exhaustion")
                return {"success": True, "type": "conversational"}
            raise HTTPException(status_code=500, detail=error)
        response_text = response_text.strip().lower()
        logger.info(f"Classification result: {response_text}")
        if response_text not in ["conversational", "database_query", "resume_query"]:
            response_text = "conversational"
        return {"success": True, "type": response_text}
    except Exception as e:
        logger.error(f"Error during classify-message: {str(e)}")
        return {"success": False, "error": str(e), "type": "conversational"}

@app.post("/api/conversational-response")
async def get_conversational_response(request: ChatRequest):
    try:
        logger.info(f"Received conversational request from user: {request.userEmail}")
        response, error = get_completion_from_azure_openai(
            DEFAULT_MODEL,
            request.message,
            temperature=0.7,
            max_tokens=1000
        )
        if error:
            if "Quota exceeded" in error:
                return {
                    "success": True,
                    "message": "Sorry, I'm unable to respond right now due to usage limits. Please try a resume-related query or contact support.",
                    "type": "conversational"
                }
            raise HTTPException(status_code=500, detail=error)
        return {"success": True, "message": response, "type": "conversational"}
    except Exception as e:
        logger.error(f"Error in conversational-response: {str(e)}")
        return {"success": False, "error": str(e), "type": "conversational"}

@app.post("/api/ask-llama")
async def ask_llama(request: ChatRequest):
    try:
        logger.info(f"Received ask-llama request from user: {request.userEmail}")
        logger.info(f"Question: {request.message}")
        table_name = None
        format_type = request.format
        question = request.message

        if "tabular format" in question.lower() or "table format" in question.lower():
            format_type = "table"
            logger.info("Format detected: table")

        if question.startswith("[Table:"):
            match = re.match(r'\[Table: ([^\]]+)\] (.+)', question)
            if match:
                table_name = match.group(1)
                question = match.group(2)
                logger.info(f"Table extracted: {table_name}")

        if table_name and table_name not in request.accessibleTables and "Admin" not in [role["name"] for role in request.userRoles]:
            logger.info(f"Permission denied for table {table_name}")
            return {"success": False, "error": f"You don't have permission to query the {table_name} table"}

        if not table_name:
            guess_prompt = f"""
You are an AI assistant.

A user asked: "{question}"

Available tables: {', '.join(request.accessibleTables)}

Based on the user's question, suggest the most relevant table name from the list.

Respond only with the table name exactly. If unsure, reply "Unknown".
"""
            table_guess, error = get_completion_from_azure_openai(DEFAULT_MODEL, guess_prompt, temperature=0.1, max_tokens=20)
            if error:
                if "Quota exceeded" in error:
                    return {
                        "success": False,
                        "error": "Cannot process database query due to usage limits. Try a resume-related query or contact support."
                    }
                raise HTTPException(status_code=500, detail=error)
            table_guess = table_guess.strip()
            if table_guess and table_guess.lower() != "unknown" and table_guess in request.accessibleTables:
                table_name = table_guess
                logger.info(f"Guessed table: {table_name}")
            else:
                return {"success": False, "error": "Please specify a table to query."}

        schema = get_table_schema(table_name)
        logger.info(f"Schema fetched for table: {table_name}")
        user_role = request.userRoles[0]["name"] if request.userRoles else None
        sql_query = get_nl2sql_response(question, table_name, schema, user_role)
        logger.info(f"SQL generated: {sql_query}")

        if sql_query.startswith("Error:"):
            return {"success": False, "error": sql_query}

        results = execute_sql_query(sql_query)
        if not results:
            return {"success": True, "results": [], "message": "No results found for your query."}

        if format_type == "table":
            return {"success": True, "results": results, "format": "table", "type": "database_query"}

        natural_language_response = convert_results_to_natural_language(results, question, table_name)
        return {"success": True, "message": natural_language_response, "format": "text", "type": "database_query"}
    except Exception as e:
        logger.error(f"Error in ask-llama: {str(e)}")
        return {"success": False, "error": str(e), "type": "database_query"}

@app.post("/api/resume-search")
async def resume_search(request: ResumeSearchRequest):
    try:
        logger.info(f"Received resume search request from user: {request.userEmail}")
        logger.info(f"Query: {request.query}")
        
        if not any(role["name"] in ["Recruiter", "Admin"] for role in request.userRoles):
            raise HTTPException(status_code=403, detail="You don't have permission to search resumes.")

        if not is_embedding_enabled:
            raise HTTPException(status_code=503, detail=f"Resume search is unavailable due to embedding client initialization failure: {embedding_error}")

        vector_db = VectorDBManager()
        search_results = vector_db.search_resumes(request.query, n_results=request.n_results)
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0]

        results_context = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            result = {
                "file_name": meta.get('file_name', 'Unknown'),
                "content": doc[:500],
                "similarity_score": 1 - dist,
                "metadata": meta
            }
            results_context.append(result)

        # Skip natural language conversion if general client is unavailable
        if not is_general_enabled:
            return {
                "success": True,
                "message": "Resume search completed, but natural language response is unavailable due to usage limits.",
                "format": "text",
                "type": "resume_query",
                "results": results_context
            }

        results_json = json.dumps(results_context, indent=2)
        prompt = f"""
You are an AI assistant specialized in resume search.

A user asked: "{request.query}"

Here are the top matching resumes:
```json
{results_json}
```

Convert these search results into a natural language response that directly answers the user's query.
Make your response conversational, friendly, and concise. Focus on key information such as candidate skills, experience, or roles that match the query.
Do not mention file names, similarity scores, or technical terms like "vector" or "embedding".
If no relevant information is found, say so politely.
"""
        response, error = get_completion_from_azure_openai(
            DEFAULT_MODEL,
            prompt,
            temperature=0.5,
            max_tokens=1000
        )
        if error:
            if "Quota exceeded" in error:
                return {
                    "success": True,
                    "message": "Resume search completed, but natural language response is unavailable due to usage limits.",
                    "format": "text",
                    "type": "resume_query",
                    "results": results_context
                }
            raise HTTPException(status_code=500, detail=error)

        return {
            "success": True,
            "message": response,
            "format": "text",
            "type": "resume_query",
            "results": results_context
        }
    except Exception as e:
        logger.error(f"Error in resume-search: {str(e)}")
        return {"success": False, "error": str(e), "type": "resume_query"}

@app.post("/api/chatbot-router")
async def chatbot_router(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message")
        user_email = body.get("userEmail")
        user_roles = body.get("userRoles", [])
        accessible_tables = body.get("accessibleTables", [])
        format_type = body.get("format", "text")

        if not user_message:
            raise ValueError("User message missing!")

        classification_response = await classify_message(
            MessageClassificationRequest(
                message=user_message,
                accessibleTables=accessible_tables,
                userEmail=user_email,
                userRoles=user_roles
            )
        )

        message_type = classification_response.get("type", "conversational")
        logger.info(f"Router classified message as: {message_type}")

        if message_type == "conversational":
            response = await get_conversational_response(
                ChatRequest(
                    message=user_message,
                    userEmail=user_email,
                    userRoles=user_roles,
                    accessibleTables=accessible_tables,
                    format=format_type
                )
            )
        elif message_type == "database_query":
            response = await ask_llama(
                ChatRequest(
                    message=user_message,
                    userEmail=user_email,
                    userRoles=user_roles,
                    accessibleTables=accessible_tables,
                    format=format_type
                )
            )
        elif message_type == "resume_query":
            response = await resume_search(
                ResumeSearchRequest(
                    query=user_message,
                    userEmail=user_email,
                    userRoles=user_roles,
                    n_results=5
                )
            )
        else:
            response = {"success": False, "error": "Unknown message type.", "type": "conversational"}
        return response
    except Exception as e:
        logger.error(f"Error in chatbot-router: {str(e)}")
        return {"success": False, "error": str(e), "type": "conversational"}

@app.get("/api/table-schema/{table_name}")
async def get_schema(table_name: str):
    try:
        logger.info(f"Getting schema for table: {table_name}")
        schema = get_table_schema(table_name)
        return {"success": True, "schema": schema}
    except Exception as e:
        logger.error(f"Error getting schema for {table_name}: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/health")
async def health_check():
    try:
        response, error = get_completion_from_azure_openai(DEFAULT_MODEL, "Say hello", temperature=0.1, max_tokens=10)
        if error and "Quota exceeded" not in error:
            raise Exception(error)
        conn, error = establish_connection()
        db_status = "connected" if conn else f"error: {error}"
        if conn:
            conn.close()
        return {
            "status": "healthy" if not error else "partially_healthy",
            "openai_connection": "working" if not error else f"error: {error}",
            "openai_response": response if response else None,
            "database_connection": db_status,
            "embedding_enabled": is_embedding_enabled,
            "api_version": "1.0.0"
        }
    except Exception as e:
        error_detail = str(e)
        if embedding_error:
            error_detail = f"{error_detail}. Azure OpenAI embedding error: {embedding_error}"
        logger.error(f"Health check error: {error_detail}")
        return {
            "status": "unhealthy",
            "error": error_detail,
            "embedding_enabled": is_embedding_enabled,
            "api_version": "1.0.0"
        }

@router.get("/internal/get-sharepoint-token", include_in_schema=False)
async def get_sharepoint_token():
    try:
        authority = f"https://login.microsoftonline.com/{SHAREPOINT_TENANT_ID}"
        app_msal = msal.ConfidentialClientApplication(
            client_id=SHAREPOINT_CLIENT_ID,
            authority=authority,
            client_credential=SHAREPOINT_CLIENT_SECRET
        )
        token_result = app_msal.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in token_result:
            raise HTTPException(status_code=500, detail=f"Token fetch failed: {token_result.get('error_description', 'Unknown error')}")
        return {"access_token": token_result["access_token"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)