from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

def get_groq_llm(model_name="mixtral-8x7b-32768", temperature=0.7):
    """Initialize and return a Groq LLM instance"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=4096
    )
