import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries=3, initial_backoff=1, backoff_factor=2):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_backoff = initial_backoff
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Max retries ({max_retries}) reached. Last error: {str(e)}")
                        raise
                    
                    logger.warning(f"Attempt {retries} failed. Retrying in {current_backoff} seconds. Error: {str(e)}")
                    time.sleep(current_backoff)
                    current_backoff *= backoff_factor
            
            return None
        return wrapper
    return decorator

def rate_limit(max_calls=60, period=60):
    """Rate limiting decorator"""
    def decorator(func):
        calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the period
            calls[:] = [call for call in calls if call > now - period]
            
            if len(calls) >= max_calls:
                wait_time = calls[0] - (now - period)
                if wait_time > 0:
                    logger.warning(f"Rate limit reached. Waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
                    calls.pop(0)
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
