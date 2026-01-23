"""
Config module - paths and default params.

Usage:
    from ecc.config import PATHS, DEFAULTS

    # Access paths
    figures_dir = PATHS.figures_dir

    # Get defaults
    seed = DEFAULTS.seed
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    """Path configuration for the project.

    root: repo root directory
    data_dir: data storage (raw/interim/processed)
    reports_dir: analysis outputs
    figures_dir: plot outputs
    """
    root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = root / "data"
    reports_dir: Path = root / "reports"
    figures_dir: Path = reports_dir / "figures"


@dataclass(frozen=True)
class Defaults:
    """Default parameters for data generation.

    Override these when calling generate_dataset() or pipeline functions.

    seed: random seed for reproducibility
    n_users: number of synthetic users
    n_weeks: weekly observations per user
    t0_week: start of exposure window
    retention_week: when retention is measured (t0 + 4)
    """
    seed: int = 7

    # Synthetic dataset size (Stage 1)
    n_users: int = 25_000
    n_weeks: int = 8

    # Retention definition
    t0_week: int = 1  # exposure window starts here
    retention_week: int = 5  # t0 + 4


PATHS = Paths()
DEFAULTS = Defaults()
