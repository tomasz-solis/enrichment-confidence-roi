from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ecc.config import DEFAULTS
from ecc.dgp.schemas import USER, USER_WEEK, validate_user_df, validate_user_week_df
from ecc.utils import set_seed


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def _zscore(x: np.ndarray) -> np.ndarray:
    mu = np.mean(x)
    sigma = np.std(x)
    if sigma == 0:
        return np.zeros_like(x)
    return (x - mu) / sigma


@dataclass(frozen=True)
class DGPParams:
    # confidence model
    alpha_c: float = 1.0
    b_f: float = 1.2
    b_c: float = 1.0
    b_e: float = 0.2
    sigma_c_week: float = 0.6

    # edit model
    alpha_e: float = -1.8
    tau_e: float = 2.0
    g_c: float = 0.8
    g_e: float = 0.4
    g_f: float = 0.3
    sigma_e: float = 0.5

    # txn volume model (optional but useful)
    alpha_n: float = 2.2
    beta_ne: float = 0.55

    # retention model
    alpha_r: float = -0.3
    delta_e: float = 1.4
    delta_f: float = 0.4
    delta_c: float = 0.1
    tau_r: float = 0.8
    kappa_r: float = 1.0
    sigma_r: float = 0.4


def generate_user_traits(
    *,
    n_users: int,
    seed: int = DEFAULTS.seed,
) -> pd.DataFrame:
    """
    Generate user-level confounders:
    - feed_quality in [0,1]
    - txn_complexity > 0
    - baseline_engagement > 0

    Also includes z-scored variants used in the DGP.
    """
    set_seed(seed)

    user_id = np.arange(1, n_users + 1)

    # feed quality: beta distribution on [0,1]
    feed_quality = np.random.beta(a=5.0, b=2.2, size=n_users)

    # positive, heavy-tailed
    txn_complexity = np.random.lognormal(mean=0.0, sigma=0.6, size=n_users)
    baseline_engagement = np.random.lognormal(mean=0.0, sigma=0.7, size=n_users)

    df = pd.DataFrame(
        {
            USER.user_id: user_id.astype(int),
            USER.feed_quality: feed_quality.astype(float),
            USER.txn_complexity: txn_complexity.astype(float),
            USER.baseline_engagement: baseline_engagement.astype(float),
        }
    )

    df[USER.feed_quality_z] = _zscore(df[USER.feed_quality].to_numpy())
    df[USER.txn_complexity_z] = _zscore(df[USER.txn_complexity].to_numpy())
    df[USER.baseline_engagement_z] = _zscore(df[USER.baseline_engagement].to_numpy())

    return df


def generate_user_week(
    df_users: pd.DataFrame,
    *,
    n_weeks: int,
    params: DGPParams = DGPParams(),
    seed: int = DEFAULTS.seed,
) -> pd.DataFrame:
    """
    Generate user-week table with:
    - confidence in [0,1]
    - edit_rate in [0,1]
    - n_txn >= 0
    """
    set_seed(seed)

    n_users = df_users.shape[0]

    # repeat users across weeks
    weeks = np.arange(1, n_weeks + 1)
    user_id_rep = np.repeat(df_users[USER.user_id].to_numpy(), n_weeks)
    week_rep = np.tile(weeks, n_users)

    # pull z-scored confounders aligned to repeated rows
    fz = np.repeat(df_users[USER.feed_quality_z].to_numpy(), n_weeks)
    cz = np.repeat(df_users[USER.txn_complexity_z].to_numpy(), n_weeks)
    ez = np.repeat(df_users[USER.baseline_engagement_z].to_numpy(), n_weeks)

    # weekly txn volume (Poisson with engagement effect)
    log_lambda = params.alpha_n + params.beta_ne * ez
    lam = np.exp(log_lambda)
    n_txn = np.random.poisson(lam=lam).astype(int)

    # confidence latent -> sigmoid
    u = np.random.normal(loc=0.0, scale=params.sigma_c_week, size=n_users * n_weeks)
    conf_latent = params.alpha_c + params.b_f * fz - params.b_c * cz + params.b_e * ez + u
    confidence = _sigmoid(conf_latent)

    # edit propensity latent -> sigmoid
    eps = np.random.normal(loc=0.0, scale=params.sigma_e, size=n_users * n_weeks)
    edit_latent = (
        params.alpha_e
        - params.tau_e * confidence
        + params.g_c * cz
        + params.g_e * ez
        + params.g_f * (-fz)
        + eps
    )
    edit_rate = _sigmoid(edit_latent)

    df = pd.DataFrame(
        {
            USER_WEEK.user_id: user_id_rep.astype(int),
            USER_WEEK.week: week_rep.astype(int),
            USER_WEEK.n_txn: n_txn,
            USER_WEEK.confidence: confidence.astype(float),
            USER_WEEK.edit_rate: edit_rate.astype(float),
        }
    )

    return df


def build_wk4_retention(
    df_users: pd.DataFrame,
    df_user_week: pd.DataFrame,
    *,
    t0_week: int = DEFAULTS.t0_week,
    retention_week: int = DEFAULTS.retention_week,
    params: DGPParams = DGPParams(),
    seed: int = DEFAULTS.seed,
) -> pd.DataFrame:
    """
    Build a user-level week+4 retention label, based on weeks t0..t0+3.

    We keep this as a synthetic "activity at week 5" indicator to mimic a lagging KPI.
    """
    set_seed(seed)

    # exposure window: weeks 1-4 relative to t0_week
    exposure_weeks = list(range(t0_week, t0_week + 4))
    df_exp = df_user_week[df_user_week[USER_WEEK.week].isin(exposure_weeks)].copy()

    # summarize exposure window per user
    agg = (
        df_exp.groupby(USER_WEEK.user_id, as_index=False)
        .agg(
            conf_mean=(USER_WEEK.confidence, "mean"),
            edit_mean=(USER_WEEK.edit_rate, "mean"),
        )
    )

    df = df_users.merge(agg, on=USER.user_id, how="left")

    # if a user has no exposure rows (shouldn't happen in v1), fill neutral values
    df["conf_mean"] = df["conf_mean"].fillna(df["conf_mean"].mean())
    df["edit_mean"] = df["edit_mean"].fillna(df["edit_mean"].mean())

    fz = df[USER.feed_quality_z].to_numpy()
    cz = df[USER.txn_complexity_z].to_numpy()
    ez = df[USER.baseline_engagement_z].to_numpy()

    nu = np.random.normal(loc=0.0, scale=params.sigma_r, size=df.shape[0])
    ret_latent = (
        params.alpha_r
        + params.delta_e * ez
        + params.delta_f * fz
        + params.delta_c * cz
        + params.tau_r * df["conf_mean"].to_numpy()
        - params.kappa_r * df["edit_mean"].to_numpy()
        + nu
    )
    p_ret = _sigmoid(ret_latent)

    wk4_retention = np.random.binomial(n=1, p=p_ret, size=df.shape[0]).astype(int)
    df[USER.wk4_retention] = wk4_retention

    # keep the extra columns (conf_mean/edit_mean) for debugging; drop later if desired
    return df


def generate_dataset(
    *,
    n_users: int = DEFAULTS.n_users,
    n_weeks: int = DEFAULTS.n_weeks,
    seed: int = DEFAULTS.seed,
    params: DGPParams = DGPParams(),
    t0_week: int = DEFAULTS.t0_week,
    retention_week: int = DEFAULTS.retention_week,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    End-to-end synthetic dataset generation:
    returns (df_users, df_user_week).

    df_users includes wk4_retention (binary) plus user traits.
    df_user_week includes weekly confidence/edit_rate/n_txn.
    """
    df_users = generate_user_traits(n_users=n_users, seed=seed)
    df_user_week = generate_user_week(df_users, n_weeks=n_weeks, params=params, seed=seed)

    df_users = build_wk4_retention(
        df_users,
        df_user_week,
        t0_week=t0_week,
        retention_week=retention_week,
        params=params,
        seed=seed,
    )

    validate_user_week_df(df_user_week)
    validate_user_df(df_users)

    return df_users, df_user_week
