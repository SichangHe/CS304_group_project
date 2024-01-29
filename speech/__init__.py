import logging
import os
from concurrent.futures import ProcessPoolExecutor
from typing import TypeVar

logging.basicConfig(level=os.environ.get("PYTHON_LOG", "WARN").upper())

_process_pool = None

T = TypeVar("T")


def process_pool():
    """Obtain a reused global process pool."""
    global _process_pool
    if _process_pool is None:
        _process_pool = ProcessPoolExecutor()
    return _process_pool
