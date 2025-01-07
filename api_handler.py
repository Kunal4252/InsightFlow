# api_handler.py
import requests
from typing import Optional, Dict, Any
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangflowAPI:
    def __init__(self):
        self.base_url = Config.BASE_API_URL
        self.langflow_id = Config.LANGFLOW_ID
        self.application_token = Config.APPLICATION_TOKEN
        
    def extract_text_from_response(self, response_data: Dict) -> str:
        """Extract the text content from the API response structure."""
        try:
            # Navigate through the response structure to get the text
            if "outputs" in response_data and len(response_data["outputs"]) > 0:
                first_output = response_data["outputs"][0]
                if "outputs" in first_output and len(first_output["outputs"]) > 0:
                    results = first_output["outputs"][0].get("results", {})
                    message = results.get("message", {})
                    return message.get("text", "No response text found")
            return "No response text found"
        except Exception as e:
            logger.error(f"Error extracting text from response: {str(e)}")
            return "Error processing response"

    def run_flow(
        self,
        message: str,
        endpoint: str = Config.FLOW_ID,
        output_type: str = "chat",
        input_type: str = "chat",
        tweaks: Optional[dict] = None
    ) -> str:  # Changed return type to str since we're returning text
        """
        Run a flow with the given message and parameters.
        
        Args:
            message: The input message for the flow
            endpoint: The endpoint or flow ID
            output_type: Type of output expected
            input_type: Type of input being sent
            tweaks: Optional configuration tweaks
            
        Returns:
            str: The extracted text response
        """
        try:
            # Ensure endpoint is not empty
            if not endpoint:
                endpoint = Config.FLOW_ID
                logger.warning(f"Empty endpoint provided, using default FLOW_ID: {endpoint}")
            
            # Construct API URL with proper endpoint
            api_url = f"{self.base_url}/lf/{self.langflow_id}/api/v1/run/{endpoint}"
            
            payload = {
                "input_value": message,
                "output_type": output_type,
                "input_type": input_type,
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.application_token:
                headers["Authorization"] = f"Bearer {self.application_token}"
            
            if tweaks:
                payload["tweaks"] = tweaks
                
            logger.info(f"Sending request to {api_url}")
            
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Extract just the text content from the response
            response_data = response.json()
            return self.extract_text_from_response(response_data)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_msg += f"\nResponse content: {e.response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise