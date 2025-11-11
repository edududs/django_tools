"""Timing utilities for measuring execution time."""

from contextlib import contextmanager
from time import perf_counter


@contextmanager
def measure_time():
    """Context manager for measuring execution time.

    Yields:
        Callable that returns elapsed time in seconds when called

    Example:
        with measure_time() as get_duration:
            # Do work here
            duration = get_duration()
    """
    start = perf_counter()
    yield lambda: perf_counter() - start

