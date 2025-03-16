import logging
from typing import List, Optional
from .groq_client import get_groq_llm

logger = logging.getLogger(__name__)

def get_rag_context(query: str, documents: List[str], max_tokens: int = 1024) -> str:
    """
    Generate context from relevant documents using RAG approach.
    
    Args:
        query: User's query
        documents: List of relevant documents
        max_tokens: Maximum tokens for context generation
        
    Returns:
        str: Generated context incorporating relevant information from documents
    """
    try:
        if not documents:
            return ""
            
        # Combine documents into a single context string
        context = "\n\n".join(documents)
        
        # Use LLM to generate focused context based on query
        llm = get_groq_llm(max_tokens=max_tokens)
        prompt = f"""
        Given the following query and document context, extract and summarize the most relevant information:
        
        Query: {query}
        
        Document Context:
        {context}
        
        Please provide a concise summary focusing on information relevant to the query.
        """
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        logger.error(f"Error generating RAG context: {str(e)}")
        return ""
