"""Paired obs/model comparison statistics on an hourly grid."""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["paired_stats"]


def paired_stats(
    obs_df: pd.DataFrame,
    mod_df: pd.DataFrame,
    var: str,
    t0: pd.Timestamp,
    t1: pd.Timestamp,
    label_var: str,
    label_window: str,
) -> dict:
    """Compute bias / RMSE / r / N on hourly-matched obs–model pairs.

    Both dataframes must have ``time`` and ``var`` columns. The merge is
    inner on the hourly-floored time. NaNs in either obs or model are
    dropped before statistics are computed.

    Returns a dict with keys: ``variable``, ``subwindow``, ``N``, ``bias``,
    ``rmse``, ``r``.
    """
    obs = obs_df[["time", var]].rename(columns={var: "obs"}).copy()
    mod = mod_df[["time", var]].rename(columns={var: "mod"}).copy()
    obs["time"] = pd.to_datetime(obs["time"]).dt.floor("h")
    mod["time"] = pd.to_datetime(mod["time"]).dt.floor("h")
    merged = obs.merge(mod, on="time", how="inner")
    merged = merged[(merged["time"] >= t0) & (merged["time"] < t1)]
    merged = merged.dropna(subset=["obs", "mod"])
    n = len(merged)
    if n < 2:
        return {
            "variable": label_var,
            "subwindow": label_window,
            "N": n,
            "bias": np.nan,
            "rmse": np.nan,
            "r": np.nan,
        }
    diff = merged["mod"] - merged["obs"]
    return {
        "variable": label_var,
        "subwindow": label_window,
        "N": n,
        "bias": float(diff.mean()),
        "rmse": float(np.sqrt((diff ** 2).mean())),
        "r": float(np.corrcoef(merged["obs"], merged["mod"])[0, 1]),
    }
