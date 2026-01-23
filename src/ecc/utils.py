"""
Utility functions for reproducibility and file ops.

Kept minimal and dependency-free to avoid circular imports.
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility.

    Sets both random and numpy seeds.
    Call at the start of any function with randomness.

    Args:
        seed: seed value
    """
    random.seed(seed)
    np.random.seed(seed)


def ensure_dir(path: Path) -> None:
    """Create directory if it doesn't exist.

    Args:
        path: directory to create
    """
    path.mkdir(parents=True, exist_ok=True)