import json
import logging
import os
import time
from typing import Dict, Any, List, Optional
import httpx
from config import settings

logger = logging.getLogger("CloudantService")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class CloudantService:
    """
    Service to handle interactions with IBM Cloudant NoSQL database using standard HTTP REST API (async).
    Uses IBM IAM Bearer tokens to support both standard and IAM-only Cloudant configurations.
    Includes a robust local file-based database fallback for demo/testing when credentials are not configured.
    """
    
    def __init__(self) -> None:
        self.url = settings.IBM_CLOUDANT_URL
        self.api_key = settings.IBM_CLOUDANT_API_KEY
        self.is_mock = False
        self.client = None
        self.local_db_path = "local_db.json"
        
        # IAM Token Caching
        self.iam_token = None
        self.token_expiry = 0
        
        self._init_connection()

    def _init_connection(self) -> None:
        """
        Initialize the connection client. If credentials are missing, falls back to mock mode.
        """
        if not self.url or not self.api_key:
            logger.warning(
                "IBM Cloudant URL or API key is missing. "
                "Cloudant service will operate in local mock database mode."
            )
            self.is_mock = True
            self._init_local_db()
            return

        try:
            logger.info("Initializing IBM Cloudant AsyncClient...")
            self.client = httpx.AsyncClient(
                base_url=self.url.rstrip("/"),
                headers={"Content-Type": "application/json"},
                timeout=15.0
            )
            logger.info("Cloudant client initialized. Testing connectivity will happen dynamically with IAM tokens.")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudant HTTP Client: {str(e)}", exc_info=True)
            self.is_mock = True
            self._init_local_db()

    def _init_local_db(self) -> None:
        """
        Initializes local JSON database file for mock mode.
        """
        if not os.path.exists(self.local_db_path):
            initial_schema = {
                "users": [],
                "sessions": {},
                "resumes": [],
                "interviews": [],
                "analytics": {}
            }
            with open(self.local_db_path, "w") as f:
                json.dump(initial_schema, f, indent=2)
            logger.info(f"Initialized mock local database at '{self.local_db_path}'")

    def _read_local_db(self) -> Dict[str, Any]:
        """Reads mock local database."""
        try:
            with open(self.local_db_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read local DB: {str(e)}")
            return {"users": [], "sessions": {}, "resumes": [], "interviews": [], "analytics": {}}

    def _write_local_db(self, db_data: Dict[str, Any]) -> None:
        """Writes mock local database."""
        try:
            with open(self.local_db_path, "w") as f:
                json.dump(db_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write local DB: {str(e)}")

    async def _get_iam_token(self) -> Optional[str]:
        """
        Fetch a fresh IAM Access Token from IBM Cloud identity services.
        """
        try:
            async with httpx.AsyncClient() as iam_client:
                resp = await iam_client.post(
                    "https://iam.cloud.ibm.com/identity/token",
                    data={
                        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                        "apikey": self.api_key
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0
                )
                if resp.status_code == 200:
                    token_data = resp.json()
                    return token_data.get("access_token")
                else:
                    logger.error(f"Failed to fetch Cloudant IAM token: {resp.status_code} - {resp.text}")
                    return None
        except Exception as e:
            logger.error(f"Error requesting IBM IAM token: {str(e)}", exc_info=True)
            return None

    async def _get_headers(self) -> Dict[str, str]:
        """
        Generate HTTP headers, refreshing IAM bearer tokens if necessary.
        """
        headers = {"Content-Type": "application/json"}
        if self.is_mock:
            return headers
            
        # Refresh if token not present or expiring in less than 5 minutes
        if not self.iam_token or time.time() > self.token_expiry - 300:
            logger.info("Refreshing IBM Cloudant IAM token...")
            token = await self._get_iam_token()
            if token:
                self.iam_token = token
                self.token_expiry = time.time() + 3600 # Cache for 1 hour
                logger.info("IBM Cloudant IAM token cached successfully.")
            else:
                logger.error("Could not obtain new IBM IAM access token. Request may fail.")
                
        if self.iam_token:
            headers["Authorization"] = f"Bearer {self.iam_token}"
            
        return headers

    async def _ensure_database(self, db_name: str) -> None:
        """
        Ensure that a Cloudant database exists. Creates it if not found.
        """
        if self.is_mock:
            return

        try:
            headers = await self._get_headers()
            # Check if database exists by querying it
            response = await self.client.get(f"/{db_name}", headers=headers)
            if response.status_code == 200:
                return
            elif response.status_code == 404:
                logger.info(f"Database '{db_name}' not found. Creating...")
                create_res = await self.client.put(f"/{db_name}", headers=headers)
                if create_res.status_code in [201, 202]:
                    logger.info(f"Database '{db_name}' created successfully.")
                else:
                    logger.error(f"Failed to create database '{db_name}': {create_res.text}")
            else:
                logger.error(f"Unexpected response code checking database '{db_name}': {response.status_code}")
        except Exception as e:
            logger.error(f"Error checking/creating database '{db_name}': {str(e)}")

    async def create_document(self, db_name: str, doc_id: str, doc_content: Dict[str, Any]) -> bool:
        """
        Create a document in a Cloudant database.
        """
        if self.is_mock:
            db_data = self._read_local_db()
            if db_name not in db_data:
                db_data[db_name] = []
            
            # For lists like users, resumes, interviews
            if isinstance(db_data[db_name], list):
                # Check duplicate
                for item in db_data[db_name]:
                    if item.get("_id") == doc_id or item.get("id") == doc_id:
                        logger.warning(f"Mock DB: Duplicate ID '{doc_id}' in '{db_name}'")
                        return False
                doc_content["_id"] = doc_id
                db_data[db_name].append(doc_content)
            # For key-value like sessions, analytics
            elif isinstance(db_data[db_name], dict):
                db_data[db_name][doc_id] = doc_content
                
            self._write_local_db(db_data)
            return True

        await self._ensure_database(db_name)
        try:
            doc_content["_id"] = doc_id
            headers = await self._get_headers()
            response = await self.client.put(f"/{db_name}/{doc_id}", json=doc_content, headers=headers)
            if response.status_code in [200, 201, 202]:
                logger.info(f"Document '{doc_id}' created in database '{db_name}'")
                return True
            else:
                logger.error(f"Failed to create document '{doc_id}' in '{db_name}': {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error creating document '{doc_id}' in '{db_name}': {str(e)}", exc_info=True)
            return False

    async def get_document(self, db_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by ID from Cloudant database.
        """
        if self.is_mock:
            db_data = self._read_local_db()
            db = db_data.get(db_name)
            if isinstance(db, list):
                for item in db:
                    if item.get("_id") == doc_id or item.get("id") == doc_id:
                        return item
            elif isinstance(db, dict):
                return db.get(doc_id)
            return None

        await self._ensure_database(db_name)
        try:
            headers = await self._get_headers()
            response = await self.client.get(f"/{db_name}/{doc_id}", headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error getting document '{doc_id}' from '{db_name}': {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving document '{doc_id}' from '{db_name}': {str(e)}", exc_info=True)
            return None

    async def update_document(self, db_name: str, doc_id: str, doc_content: Dict[str, Any]) -> bool:
        """
        Update an existing document in Cloudant database (requires matching _rev key).
        """
        if self.is_mock:
            db_data = self._read_local_db()
            db = db_data.get(db_name)
            if isinstance(db, list):
                for i, item in enumerate(db):
                    if item.get("_id") == doc_id or item.get("id") == doc_id:
                        db[i] = doc_content
                        db[i]["_id"] = doc_id
                        self._write_local_db(db_data)
                        return True
            elif isinstance(db, dict):
                db_data[db_name][doc_id] = doc_content
                self._write_local_db(db_data)
                return True
            return False

        await self._ensure_database(db_name)
        try:
            # First fetch to get latest _rev
            current_doc = await self.get_document(db_name, doc_id)
            if not current_doc:
                logger.error(f"Update failed: Document '{doc_id}' not found in '{db_name}'")
                return False
                
            doc_content["_rev"] = current_doc["_rev"]
            doc_content["_id"] = doc_id
            
            headers = await self._get_headers()
            response = await self.client.put(f"/{db_name}/{doc_id}", json=doc_content, headers=headers)
            if response.status_code in [200, 201, 202]:
                logger.info(f"Document '{doc_id}' updated in database '{db_name}'")
                return True
            else:
                logger.error(f"Failed to update document '{doc_id}' in '{db_name}': {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error updating document '{doc_id}' in '{db_name}': {str(e)}", exc_info=True)
            return False

    async def delete_document(self, db_name: str, doc_id: str) -> bool:
        """
        Deletes a document from a Cloudant database.
        """
        if self.is_mock:
            db_data = self._read_local_db()
            db = db_data.get(db_name)
            if isinstance(db, list):
                for i, item in enumerate(db):
                    if item.get("_id") == doc_id or item.get("id") == doc_id:
                        db.pop(i)
                        self._write_local_db(db_data)
                        return True
            elif isinstance(db, dict):
                if doc_id in db_data[db_name]:
                    db_data[db_name].pop(doc_id)
                    self._write_local_db(db_data)
                    return True
            return False

        await self._ensure_database(db_name)
        try:
            current_doc = await self.get_document(db_name, doc_id)
            if not current_doc:
                return True # Already deleted or not found
                
            rev = current_doc["_rev"]
            headers = await self._get_headers()
            response = await self.client.delete(f"/{db_name}/{doc_id}", params={"rev": rev}, headers=headers)
            if response.status_code in [200, 202]:
                logger.info(f"Document '{doc_id}' deleted from database '{db_name}'")
                return True
            else:
                logger.error(f"Failed to delete document '{doc_id}' from '{db_name}': {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error deleting document '{doc_id}' from '{db_name}': {str(e)}", exc_info=True)
            return False

    async def query_documents(self, db_name: str, query_selector: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query Cloudant documents using declarative selectors (Mango queries).
        """
        if self.is_mock:
            db_data = self._read_local_db()
            db = db_data.get(db_name, [])
            if not isinstance(db, list):
                return []
                
            selector = query_selector.get("selector", {})
            results = []
            
            for doc in db:
                match = True
                for key, val in selector.items():
                    if doc.get(key) != val:
                        match = False
                        break
                if match:
                    results.append(doc)
            return results

        await self._ensure_database(db_name)
        try:
            headers = await self._get_headers()
            response = await self.client.post(f"/{db_name}/_find", json=query_selector, headers=headers)
            if response.status_code == 200:
                return response.json().get("docs", [])
            else:
                logger.error(f"Failed to query database '{db_name}': {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error querying database '{db_name}': {str(e)}", exc_info=True)
            return []

    async def shutdown(self) -> None:
        """
        Close the HTTP client session.
        """
        if self.client:
            await self.client.aclose()
            logger.info("Cloudant HTTP client connection closed.")
