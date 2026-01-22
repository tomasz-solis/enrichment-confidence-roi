"""
Central configuration for paths and defaults.

Imports:
    from ecc.config import PATHS, DEFAULTS

Example:
    # Use default paths
    figures_dir = PATHS.figures_dir

    # Use default parameters
    seed = DEFAULTS.seed
    n_users = DEFAULTS.n_users
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    """
    File system paths relative to repository root.

    Attributes:
        root: Repository root (detected from this file).
        data_dir: Where data lives (raw, interim, processed).
        reports_dir: Where analysis outputs go.
        figures_dir: Where plots are saved.
    """
    root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = root / "data"
    reports_dir: Path = root / "reports"
    figures_dir: Path = reports_dir / "figures"


@dataclass(frozen=True)
class Defaults:
    """
    Default parameters for synthetic data generation and analysis.

    These values produce realistic behavior and ensure reproducibility.
    Override them when calling generator or pipeline functions if needed.

    Attributes:
        seed: Random seed for reproducibility across runs.
        n_users: Number of synthetic users to generate.
        n_weeks: Number of weekly observations per user.
        t0_week: First week of the exposure window for retention.
        retention_week: Week at which retention is measured (t0 + 4).
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
