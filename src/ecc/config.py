from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = root / "data"
    reports_dir: Path = root / "reports"
    figures_dir: Path = reports_dir / "figures"


@dataclass(frozen=True)
class Defaults:
    seed: int = 7

    # Synthetic dataset size (Stage 1)
    n_users: int = 25_000
    n_weeks: int = 8

    # Retention definition
    t0_week: int = 1  # exposure window starts here
    retention_week: int = 5  # t0 + 4


PATHS = Paths()
DEFAULTS = Defaults()
