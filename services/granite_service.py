import logging
from typing import Dict, Any, Optional
from config import settings
from engine import GraniteEngine

logger = logging.getLogger("GraniteService")

class GraniteService:
    """
    GraniteService acts as a wrapper around the GraniteEngine to integrate with FastAPI services.
    Requires valid IBM Cloud credentials (API key and project ID) — no mock/fallback mode.
    All question generation, evaluation, and scoring is handled by the live IBM watsonx.ai API.
    """
    
    def __init__(self) -> None:
        self.engine = None
        self._init_engine()

    def _init_engine(self) -> None:
        """
        Initialize the core GraniteEngine using configurations from settings.
        """
        api_key = settings.IBM_CLOUD_API_KEY
        project_id = settings.IBM_PROJECT_ID
        endpoint_url = settings.IBM_ENDPOINT_URL
        model_id = settings.IBM_MODEL_ID

        if not api_key or not project_id:
            logger.error(
                "IBM watsonx.ai credentials (api_key or project_id) are missing in configuration. "
                "The AI features (question generation, evaluation, scoring) will NOT work. "
                "Please set IBM_CLOUD_API_KEY and IBM_PROJECT_ID in your .env file."
            )
            return

        try:
            logger.info(f"Initializing GraniteEngine with model '{model_id}'...")
            self.engine = GraniteEngine(
                api_key=api_key,
                project_id=project_id,
                endpoint_url=endpoint_url,
                model_id=model_id
            )
            logger.info("GraniteEngine successfully integrated with GraniteService.")
        except Exception as e:
            logger.error(f"Error initializing GraniteEngine inside service: {str(e)}", exc_info=True)
            self.engine = None

    def generate(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate text using the live IBM watsonx.ai Granite engine.
        Raises RuntimeError if the engine is not available (missing credentials).
        Propagates API errors so callers handle them properly.
        
        Args:
            prompt (str): Text prompt.
            params (Optional[Dict[str, Any]]): Inference parameters.
            
        Returns:
            str: Generated text content.
            
        Raises:
            RuntimeError: If IBM credentials are missing or engine not initialized.
        """
        if not self.engine:
            raise RuntimeError(
                "IBM watsonx.ai engine is not initialized. "
                "Please set IBM_CLOUD_API_KEY and IBM_PROJECT_ID in your .env file."
            )
        
        try:
            result = self.engine.generate(prompt, params)
            if not result or not result.strip():
                raise ValueError("IBM watsonx.ai returned an empty response. Please retry.")
            return result
        except Exception as e:
            logger.error(f"IBM watsonx.ai generation failed: {str(e)}", exc_info=True)
            raise
