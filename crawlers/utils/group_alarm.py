import functools
import traceback
from logging import DEBUG

def catch_except(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            error_info = traceback.format_exc()
            if DEBUG:
                print(error_info)
    return wrapper

