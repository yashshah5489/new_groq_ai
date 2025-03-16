import re
import html
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def sanitize_input(text: str) -> str:
    """
    Sanitizes user input to prevent injection attacks.
    
    Args:
        text: The user input to sanitize
        
    Returns:
        str: The sanitized text
    """
    if not isinstance(text, str):
        return ""
        
    # Escape HTML entities
    text = html.escape(text)
    
    # Remove any potential script tags or other malicious content
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    return text.strip()

def retry_with_backoff(max_retries=3, initial_backoff=1, backoff_factor=2):
    """
    Decorator for retrying function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        backoff_factor: Factor by which to increase backoff time on each retry
        
    Returns:
        The wrapped function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            backoff = initial_backoff
            last_exception = None
            
            for retry in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if retry == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                        
                    logger.warning(f"Retry {retry + 1}/{max_retries} after exception: {str(e)}")
                    time.sleep(backoff)
                    backoff *= backoff_factor
                    
        return wrapper
    return decorator

def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """
    Truncates text to the specified maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the truncated text
        add_ellipsis: Whether to add an ellipsis (...) at the end
        
    Returns:
        str: The truncated text
    """
    if not text or len(text) <= max_length:
        return text
        
    truncated = text[:max_length].rstrip()
    
    if add_ellipsis:
        truncated += "..."
        
    return truncated

def rate_limit(max_calls: int, period: int = 60):
    """
    Decorator for rate limiting function calls.
    
    Args:
        max_calls: Maximum number of calls allowed in the period
        period: Time period in seconds
        
    Returns:
        The wrapped function
    """
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Remove calls outside the time window
            while calls and calls[0] < current_time - period:
                calls.pop(0)
                
            if len(calls) >= max_calls:
                wait_time = calls[0] + period - current_time
                logger.warning(f"Rate limit exceeded. Waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
                # Recalculate current time after waiting
                current_time = time.time()
                
            calls.append(current_time)
            return func(*args, **kwargs)
            
        return wrapper
    return decorator