import functools
import psutil
import time

def memory_limited_cache(max_memory_mb=100):
    """
    Cache decorator that clears itself when memory usage exceeds the specified limit.

    Args:
        max_memory_mb (int): Maximum memory usage in megabytes before clearing the cache.

    Returns:
        function: Decorated function.
    """

    def decorator(func):
        @functools.cache
        def wrapper(*args, **kwargs):
            # Check memory usage and clear cache if necessary
            memory_usage = psutil.virtual_memory().used / (1024 ** 2)
            if memory_usage > max_memory_mb:
                wrapper.cache_clear()
            return func(*args, **kwargs)

        return wrapper

    return decorator

# Example usage
@memory_limited_cache(max_memory_mb=500)
@functools.cache
def my_test(msg:str):
    # Your expensive function here
    return f"Hello, world! {msg}"
if __name__ =="__main__":
    # Call the function
    result = my_test("AAAAA")
    result1 = my_test("AAAAA")
    print(result)