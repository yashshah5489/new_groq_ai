import functools
import time
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

def retry_with_backoff(max_retries: int = 3, initial_backoff: int = 1, backoff_factor: int = 2):
    """
    Retry decorator with exponential backoff
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            backoff = initial_backoff
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    time.sleep(backoff)
                    backoff *= backoff_factor
            raise RuntimeError("Max retries exceeded")
        return wrapper
    return decorator

def rate_limit(max_calls: int, period: int):
    """
    Rate limiting decorator
    """
    calls = []
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            now = time.time()
            calls[:] = [t for t in calls if now - t < period]
            if len(calls) >= max_calls:
                raise RuntimeError(f"Rate limit exceeded: {max_calls} calls per {period} seconds")
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
