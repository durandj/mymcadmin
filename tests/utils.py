import asyncio
import functools

def run_async(f):
    if not asyncio.iscoroutinefunction(f):
        raise RuntimeError('Test function is not a coroutine')

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(f(*args, **kwargs))
        event_loop.close()

    return wrapper

