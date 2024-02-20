import logging
import os
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray

logging.basicConfig(level=os.environ.get("PYTHON_LOG", "WARN").upper())

T = TypeVar("T")

FloatArray = NDArray[np.float32]
DoubleArray = NDArray[np.float64]
