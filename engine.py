import logging
from typing import Dict, Any, Optional
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# Configure logging
logger = logging.getLogger("GraniteEngine")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class GraniteEngine:
    """
    GraniteEngine encapsulates all LLM operations using the official IBM watsonx SDK.
    It connects to the ibm/granite-3-8b-instruct model and processes prompts 
    for question generation, answer evaluation, resume parsing, and summary generation.
    """
    
    def __init__(self, api_key: str, project_id: str, endpoint_url: str = "https://us-south.ml.cloud.ibm.com", model_id: str = "ibm/granite-8b-code-instruct"):
        """
        Initialize the GraniteEngine with IBM Cloud credentials and project ID.
        
        Args:
            api_key (str): IBM Cloud API Key for watsonx services.
            project_id (str): Watsonx project identifier.
            endpoint_url (str): Regional endpoint for watsonx.ai (e.g. us-south, eu-de).
            model_id (str): IBM Watsonx Model ID.
        """
        self.api_key = api_key
        self.project_id = project_id
        self.endpoint_url = endpoint_url
        self.model_id = model_id
        
        self.credentials = {
            "url": self.endpoint_url,
            "apikey": self.api_key
        }
        
        self._init_model()

    def _init_model(self) -> None:
        """
        Instantiate the ModelInference client from ibm_watsonx_ai.
        Raises an exception if initialization fails.
        """
        try:
            logger.info("Initializing IBM Granite ModelInference...")
            self.model = ModelInference(
                model_id=self.model_id,
                credentials=self.credentials,
                project_id=self.project_id
            )
            logger.info("IBM Granite ModelInference initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize IBM Granite ModelInference: {str(e)}", exc_info=True)
            raise e

    def _map_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper method to map standard pythonic API parameters to watsonx SDK GenParams.
        
        Args:
            params (Dict[str, Any]): Dictionary of parameter settings.
            
        Returns:
            Dict[str, Any]: Mapped parameters for the IBM Watsonx SDK.
        """
        mapped = {}
        
        # Mapping decoding method
        decoding_method = params.get("decoding_method", "greedy")
        mapped[GenParams.DECODING_METHOD] = decoding_method
        
        # Only map temperature and sampling properties if not using greedy decoding
        if decoding_method != "greedy":
            if "temperature" in params:
                mapped[GenParams.TEMPERATURE] = float(params["temperature"])
            if "top_p" in params:
                mapped[GenParams.TOP_P] = float(params["top_p"])
            if "top_k" in params:
                mapped[GenParams.TOP_K] = int(params["top_k"])
        else:
            # If greedy, enforce temperature=0.0 or omit to prevent SDK configuration conflicts
            mapped[GenParams.TEMPERATURE] = 0.0

        if "max_new_tokens" in params:
            mapped[GenParams.MAX_NEW_TOKENS] = int(params["max_new_tokens"])
        else:
            mapped[GenParams.MAX_NEW_TOKENS] = 1024
            
        if "min_new_tokens" in params:
            mapped[GenParams.MIN_NEW_TOKENS] = int(params["min_new_tokens"])
        else:
            mapped[GenParams.MIN_NEW_TOKENS] = 1

        if "stop_sequences" in params:
            mapped[GenParams.STOP_SEQUENCES] = params["stop_sequences"]

        return mapped

    def generate(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate response from the IBM Granite instruction model using the provided prompt.
        
        Args:
            prompt (str): The structured string prompt to feed the model.
            params (Optional[Dict[str, Any]]): Optional custom inference parameters.
            
        Returns:
            str: Generated text response.
        """
        try:
            input_params = params if params is not None else {}
            mapped_params = self._map_params(input_params)
            
            logger.info("Executing Granite inference generation...")
            response = self.model.generate_text(prompt=prompt, params=mapped_params)
            logger.info("Inference generation completed successfully.")
            return response
        except Exception as e:
            logger.error(f"Error during Granite generation: {str(e)}", exc_info=True)
            raise e
