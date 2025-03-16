from langchain.llms.base import LLM
from typing import Dict, Any, List, Optional
from .groq_client import call_groq_api
from .utils import retry_with_backoff
import logging

logger = logging.getLogger(__name__)

class GroqLLM(LLM):
    """
    LangChain wrapper for the Groq API.
    """
    
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 1024
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.7, max_tokens: int = 1024):
        """
        Initialize the GroqLLM.
        
        Args:
            model_name: Name of the Groq model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
        """
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"Initialized GroqLLM with model: {model_name}")
    
    @property
    def _llm_type(self) -> str:
        """
        Return the type of LLM.
        """
        return "groq_llm"
    
    @retry_with_backoff(max_retries=3, initial_backoff=1, backoff_factor=2)
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Call the Groq API with the given prompt.
        
        Args:
            prompt: The prompt to send to the API
            stop: Optional list of stop sequences
            
        Returns:
            str: The generated text
        """
        logger.debug(f"Calling Groq API with prompt length: {len(prompt)}")
        
        try:
            result = call_groq_api(
                prompt=prompt, 
                model=self.model_name,
                max_tokens=self.max_tokens, 
                temperature=self.temperature,
                stop_sequences=stop
            )
            logger.debug(f"Received response from Groq API: {result[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            raise
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """
        Return identifying parameters.
        """
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def __str__(self) -> str:
        """
        String representation of the LLM.
        """
        return f"GroqLLM(model={self.model_name}, temperature={self.temperature})"