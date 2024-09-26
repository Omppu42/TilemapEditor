import time, os
from util_logger import logger
from functools import wraps

import settings




def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        rv = func(*args, **kwargs)

        caller_path = os.path.abspath(func.__globals__["__file__"])
        caller_path = os.path.relpath(caller_path, os.getcwd()) #get path relative to cwd
        
        total_time = round(time.time() - start_time, 4)
        logger.log(f"Running function '{func.__name__}' at '{caller_path}' in {total_time} seconds")
        return rv
    
    return wrapper
