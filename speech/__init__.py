import logging
import os
from typing import TypeVar

logging.basicConfig(level=os.environ.get("PYTHON_LOG", "WARN").upper())

T = TypeVar("T")
