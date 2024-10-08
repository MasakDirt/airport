import time
from typing import Callable

import psycopg


def reconnect(max_retries: int = 5, delay: int = 10) -> Callable:
    def decorator(func: Callable) -> Callable:
        def inner(*args, **kwargs):
            retry = 0
            while max_retries is not None and retry <= max_retries:
                try:
                    func(*args, **kwargs)
                    break
                except psycopg.OperationalError:
                    retry += 1
                    print(
                        f"Database connection failed! Trying to reconnect "
                        f"{retry}/{max_retries}"
                    )
                    time.sleep(delay)
            else:
                print("Cannot connect to database!")

        return inner

    return decorator
