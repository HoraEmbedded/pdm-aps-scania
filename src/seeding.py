"""Global seeding, required by ENF03."""

import os
import random

import numpy as np

from src.config import SEED


def set_seed(seed: int = SEED) -> int:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
    except ImportError:
        pass

    return seed
