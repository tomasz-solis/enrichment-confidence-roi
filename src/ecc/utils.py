"""
Shared utilities for reproducibility and file management.

These are minimal helpers used throughout the project. Keep this module
dependency-free to avoid circular imports.
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np


def set_seed(seed: int) -> None:
    """
    Set random seeds for reproducibility.

    This sets seeds for both Python's random module and numpy.
    Call this at the start of any stochastic function.

    Args:
        seed: Integer seed value.

    Example:
        >>> set_seed(7)
        >>> np.random.rand(3)  # Will be the same every time with seed=7
    """
    random.seed(seed)
    np.random.seed(seed)


def ensure_dir(path: Path) -> None:
    """
    Create a directory if it doesn't exist.

    Args:
        path: Directory path to create.

    Example:
        >>> ensure_dir(PATHS.figures_dir)
    """
    path.mkdir(parents=True, exist_ok=True)