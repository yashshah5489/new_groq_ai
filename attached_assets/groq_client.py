import requests
import os
import json
import logging
from typing import Optional, List, Dict, Any
from .utils import rate_limit
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# print(GROQ_API_KEY)
GROQ_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

logger = logging.getLogger(__name__)

@rate_limit(max_calls=6, period=60)  # Limit to 60 calls per minute
def call_groq_api(
    prompt: str, 
    model: str = "llama-3.3-70b-versatile", 
    max_tokens: int = 1024, 
    temperature: float = 0.7,
    stop_sequences: Optional[List[str]] = None,
    system_prompt: Optional[str] = None
) -> str:
    """
    Call the Groq API with the given prompt.
    
    Args:
        prompt: The user prompt
        model: The model to use
        max_tokens: Maximum number of tokens to generate
        temperature: Temperature parameter for generation (0.0 to 1.0)
        stop_sequences: Optional list of stop sequences
        system_prompt: Optional system prompt
        
    Returns:
        str: The generated text
        
    Raises:
        ValueError: If API key is missing
        requests.RequestException: If there's an error with the request
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")
        
    messages = []
    
    # Add system message if provided
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        
    # Add user message
    messages.append({"role": "user", "content": prompt})
    
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    if stop_sequences:
        payload["stop"] = stop_sequences
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    try:
        logger.info(f"Calling Groq API with model {model}")
        response = requests.post(
            GROQ_API_ENDPOINT, 
            headers=headers, 
            json=payload,
            timeout=30  # 30 second timeout
        )
        response.raise_for_status()
        result = response.json()
        
        # Log token usage
        if "usage" in result:
            usage = result["usage"]
            logger.info(
                f"Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                f"Completion: {usage.get('completion_tokens', 0)}, "
                f"Total: {usage.get('total_tokens', 0)}"
            )
            
        # Extract the generated text from the response
        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return generated_text
        
    except requests.RequestException as e:
        logger.error(f"Request error calling Groq API: {str(e)}")
        
        # Check if we received a response with error details
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Groq API error details: {json.dumps(error_detail)}")
            except:
                logger.error(f"Groq API error status code: {e.response.status_code}")
                
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error calling Groq API: {str(e)}")
        raise