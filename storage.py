import ibm_boto3
from ibm_botocore.client import Config
import logging
from typing import BinaryIO, Optional
from config import settings

logger = logging.getLogger("COSStorage")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class COSStorageService:
    """
    Service to handle interactions with IBM Cloud Object Storage (COS) using ibm-cos-sdk.
    Used to upload/download resumes and exported PDF reports.
    """
    def __init__(self) -> None:
        self.api_key = settings.IBM_COS_API_KEY
        self.endpoint = settings.IBM_COS_ENDPOINT
        self.bucket = settings.IBM_COS_BUCKET
        self.cos_client = None
        self._init_client()

    def _init_client(self) -> None:
        """
        Initialize the IBM COS client. Falls back to mock operations 
        if required environment configurations are missing.
        """
        if not self.api_key or not self.endpoint or not self.bucket:
            logger.warning(
                "IBM COS credentials or bucket name are missing in config. "
                "COS service will operate in mock mode."
            )
            return

        try:
            logger.info("Initializing IBM COS client connection...")
            self.cos_client = ibm_boto3.client(
                "s3",
                ibm_api_key_id=self.api_key,
                endpoint_url=self.endpoint,
                config=Config(signature_version="oauth")
            )
            logger.info("IBM COS client connection initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize IBM COS client: {str(e)}", exc_info=True)
            self.cos_client = None

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> Optional[str]:
        """
        Uploads a binary file stream to the configured IBM COS bucket.
        
        Args:
            file_obj (BinaryIO): Binary file stream of the document.
            object_name (str): Unique name/key for the uploaded document in COS.
            
        Returns:
            Optional[str]: Access URL of the uploaded object, or None if the upload failed.
        """
        if not self.cos_client:
            logger.warning("IBM COS client not initialized. Falling back to local mock upload.")
            # For testing/demo stability when Cloud credentials are not yet entered,
            # we write to a temporary file locally so the app keeps working seamlessly.
            import os
            try:
                os.makedirs("uploads", exist_ok=True)
                local_path = os.path.join("uploads", object_name)
                with open(local_path, "wb") as f:
                    f.write(file_obj.read())
                logger.info(f"Mock upload successful. Saved locally: {local_path}")
                return local_path
            except Exception as ex:
                logger.error(f"Mock upload failed: {str(ex)}")
                return None

        try:
            logger.info(f"Uploading file '{object_name}' to IBM COS bucket '{self.bucket}'...")
            self.cos_client.upload_fileobj(file_obj, self.bucket, object_name)
            
            # Construct the file URL (Standard S3/COS structure)
            file_url = f"{self.endpoint}/{self.bucket}/{object_name}"
            logger.info(f"File uploaded successfully to IBM COS. Target URL: {file_url}")
            return file_url
        except Exception as e:
            logger.error(f"Error occurred while uploading to IBM COS: {str(e)}", exc_info=True)
            return None

    def download_file(self, object_name: str) -> Optional[bytes]:
        """
        Downloads a file's binary content from the IBM COS bucket.
        
        Args:
            object_name (str): Name/key of the document in COS.
            
        Returns:
            Optional[bytes]: File bytes if downloaded successfully, None otherwise.
        """
        if not self.cos_client:
            logger.warning("IBM COS client not initialized. Falling back to local mock download.")
            import os
            local_path = os.path.join("uploads", object_name)
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    return f.read()
            logger.error(f"Mock download target not found locally: {local_path}")
            return None

        try:
            logger.info(f"Downloading file '{object_name}' from IBM COS...")
            response = self.cos_client.get_object(Bucket=self.bucket, Key=object_name)
            file_bytes = response["Body"].read()
            logger.info("File downloaded successfully from IBM COS.")
            return file_bytes
        except Exception as e:
            logger.error(f"Error occurred while downloading from IBM COS: {str(e)}", exc_info=True)
            return None

    def delete_file(self, object_name: str) -> bool:
        """
        Deletes a file from the IBM COS bucket.
        
        Args:
            object_name (str): Name/key of the document in COS.
            
        Returns:
            bool: True if deleted successfully or not found, False if delete action fails.
        """
        if not self.cos_client:
            logger.warning("IBM COS client not initialized. Falling back to local mock delete.")
            import os
            local_path = os.path.join("uploads", object_name)
            if os.path.exists(local_path):
                os.remove(local_path)
                logger.info(f"Mock delete successful. Removed locally: {local_path}")
                return True
            return False

        try:
            logger.info(f"Deleting file '{object_name}' from IBM COS...")
            self.cos_client.delete_object(Bucket=self.bucket, Key=object_name)
            logger.info(f"File '{object_name}' deleted successfully from IBM COS.")
            return True
        except Exception as e:
            logger.error(f"Error occurred while deleting from IBM COS: {str(e)}", exc_info=True)
            return False
