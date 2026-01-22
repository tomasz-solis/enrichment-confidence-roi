from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class UserCols:
    user_id: str = "user_id"
    feed_quality: str = "feed_quality"
    txn_complexity: str = "txn_complexity"
    baseline_engagement: str = "baseline_engagement"
    feed_quality_z: str = "feed_quality_z"
    txn_complexity_z: str = "txn_complexity_z"
    baseline_engagement_z: str = "baseline_engagement_z"
    wk4_retention: str = "wk4_retention"


@dataclass(frozen=True)
class UserWeekCols:
    user_id: str = "user_id"
    week: str = "week"
    confidence: str = "confidence"
    edit_rate: str = "edit_rate"
    n_txn: str = "n_txn"


USER = UserCols()
USER_WEEK = UserWeekCols()


def _require_columns(df: pd.DataFrame, cols: Iterable[str], *, name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: missing required columns: {missing}")


def _require_no_nulls(df: pd.DataFrame, cols: Iterable[str], *, name: str) -> None:
    null_cols = [c for c in cols if df[c].isna().any()]
    if null_cols:
        raise ValueError(f"{name}: found nulls in columns: {null_cols}")


def _require_range(
    df: pd.DataFrame, col: str, *, lo: float, hi: float, name: str
) -> None:
    bad = df[(df[col] < lo) | (df[col] > hi)]
    if not bad.empty:
        raise ValueError(
            f"{name}: column '{col}' out of range [{lo}, {hi}] for {len(bad)} rows"
        )


def validate_user_df(df_users: pd.DataFrame) -> None:
    required = [
        USER.user_id,
        USER.feed_quality,
        USER.txn_complexity,
        USER.baseline_engagement,
        USER.feed_quality_z,
        USER.txn_complexity_z,
        USER.baseline_engagement_z,
        USER.wk4_retention,
    ]
    _require_columns(df_users, required, name="users")
    _require_no_nulls(df_users, required, name="users")

    # basic sanity
    _require_range(df_users, USER.feed_quality, lo=0.0, hi=1.0, name="users")
    _require_range(df_users, USER.wk4_retention, lo=0.0, hi=1.0, name="users")


def validate_user_week_df(df_user_week: pd.DataFrame) -> None:
    required = [
        USER_WEEK.user_id,
        USER_WEEK.week,
        USER_WEEK.confidence,
        USER_WEEK.edit_rate,
        USER_WEEK.n_txn,
    ]
    _require_columns(df_user_week, required, name="user_week")
    _require_no_nulls(df_user_week, required, name="user_week")

    _require_range(df_user_week, USER_WEEK.confidence, lo=0.0, hi=1.0, name="user_week")
    _require_range(df_user_week, USER_WEEK.edit_rate, lo=0.0, hi=1.0, name="user_week")

    if (df_user_week[USER_WEEK.week] < 1).any():
        raise ValueError("user_week: 'week' must start at 1")
    if (df_user_week[USER_WEEK.n_txn] < 0).any():
        raise ValueError("user_week: 'n_txn' must be non-negative")
