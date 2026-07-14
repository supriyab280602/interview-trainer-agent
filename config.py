import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings and environment variables management using Pydantic Settings v2.
    It automatically loads variables from a .env file and throws validation errors if types mismatch.
    """
    # IBM watsonx.ai Credentials
    IBM_CLOUD_API_KEY: str = ""
    IBM_PROJECT_ID: str = ""
    IBM_ENDPOINT_URL: str = "https://us-south.ml.cloud.ibm.com"
    IBM_MODEL_ID: str = "ibm/granite-8b-code-instruct"

    # IBM Cloudant Configuration
    IBM_CLOUDANT_URL: str = ""
    IBM_CLOUDANT_API_KEY: str = ""

    # IBM Cloud Object Storage Configuration
    IBM_COS_API_KEY: str = ""
    IBM_COS_ENDPOINT: str = ""
    IBM_COS_BUCKET: str = ""

    # Application Security & Info
    SECRET_KEY: str = "super-secret-session-key-12345"
    APP_NAME: str = "IBM Interview Trainer Agent"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()
# Reload trigger

