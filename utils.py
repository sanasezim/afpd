import time
import functools
import logging

def log_execution(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logging.info(f"Function {func.__name__} executed in {duration:.2f}s")
        return result
    return async_wrapper


def log_sync_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logging.info(f"Function {func.__name__} executed in {duration:.2f}s")
        return result
    return wrapper