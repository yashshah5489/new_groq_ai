import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class GroqLLM:
    def __init__(self, temperature=0.7, max_tokens=1024):
        """Initialize Groq LLM with specified parameters"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
            
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="mixtral-8x7b-32768",
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def invoke(self, prompt: str) -> str:
        """Send a prompt to the LLM and get the response"""
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            logger.error(f"Error invoking Groq LLM: {str(e)}")
            raise
