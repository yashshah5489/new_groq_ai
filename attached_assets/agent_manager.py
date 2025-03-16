from .generic_advice_agent import get_generic_advice
from .portfolio_agent import get_portfolio_advice
from .domain_agent import get_domain_advice
from .utils import sanitize_input
import logging

logger = logging.getLogger(__name__)

def get_agent_advice(task_type: str, **kwargs) -> str:
    """
    Routes the request to the appropriate specialized agent.
    
    Args:
        task_type: "generic", "portfolio", or "domain"
        kwargs: contains required parameters for each agent
        
    Returns:
        str: The generated advice
        
    Raises:
        ValueError: If an invalid task type is provided
        Exception: If there's an error during advice generation
    """
    # Validate task type
    valid_task_types = ["generic", "portfolio", "domain"]
    if task_type not in valid_task_types:
        error_msg = f"Invalid task type: {task_type}. Valid options are: {', '.join(valid_task_types)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    # Extract and sanitize common parameters
    context = sanitize_input(kwargs.get("context", ""))
    user_input = sanitize_input(kwargs.get("user_input", ""))
    temperature = float(kwargs.get("temperature", 0.7))
    max_tokens = int(kwargs.get("max_tokens", 1024))
    
    # Log the request
    logger.info(f"Processing {task_type} advice request: {user_input[:100]}...")
    
    try:
        if task_type == "generic":
            return get_generic_advice(
                context=context, 
                user_input=user_input,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif task_type == "portfolio":
            portfolio_details = sanitize_input(kwargs.get("portfolio_details", ""))
            return get_portfolio_advice(
                portfolio_details=portfolio_details, 
                context=context, 
                user_input=user_input,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif task_type == "domain":
            domain_details = sanitize_input(kwargs.get("domain_details", ""))
            return get_domain_advice(
                domain_details=domain_details, 
                context=context, 
                user_input=user_input,
                temperature=temperature,
                max_tokens=max_tokens
            )
    except Exception as e:
        error_msg = f"Error generating {task_type} advice: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg)