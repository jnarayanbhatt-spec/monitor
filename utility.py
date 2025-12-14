import time
import functools

def timeit(func):
    """Decorator to measure and print the execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.4f} seconds to execute")
        return result, elapsed_time
    return wrapper


# Example usage:
@timeit
def sample_function(n):
    """Sample function that sleeps for n seconds."""
    time.sleep(n)
    return f"Slept for {n} seconds"


if __name__ == "__main__":
    sample_function(2)