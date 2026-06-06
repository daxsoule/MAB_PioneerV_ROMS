"""Mixed-layer depth from a single profile via a fixed threshold.

Used by notebook 04 (`04_mixed_layer_response.ipynb`). Moved here per
constitution's Testing principle — non-trivial logic gets pytest coverage.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["mld_threshold"]


def mld_threshold(
    df_prof: pd.DataFrame,
    var: str,
    thresh: float,
    ref_depth: float = 25.0,
) -> tuple[float, str]:
    """Compute MLD from a depth-sorted profile via a fixed threshold.

    Walks downward from ``ref_depth`` and returns the first depth where
    ``|var - var(ref_depth)|`` reaches ``thresh``. Returns ``(mld_m, code)``
    where ``code`` is one of:

    - ``'ok'`` — threshold reached within the profile; MLD is reliable.
    - ``'atmin'`` — threshold already exceeded at ``ref_depth``; reported
      MLD equals ``ref_depth``, a lower bound (true MLD is shallower).
    - ``'nocrit'`` — threshold never reached; reported MLD is ``NaN``
      (true MLD is deeper than the deepest sample).
    - ``'nodata'`` — too few valid samples to compute.

    Parameters
    ----------
    df_prof : pd.DataFrame
        One profile with columns ``depth`` and the variable named by ``var``.
    var : str
        Column name to threshold on (e.g. ``'sigma_theta'`` or ``'T'``).
    thresh : float
        Threshold magnitude in the variable's units.
    ref_depth : float
        Reference depth (m, positive down). Default ``25.0`` per spec 001.
    """
    prof = df_prof.dropna(subset=[var]).sort_values("depth").reset_index(drop=True)
    if len(prof) < 3:
        return np.nan, "nodata"

    below_ref = prof[prof["depth"] >= ref_depth].reset_index(drop=True)
    if below_ref.empty:
        return np.nan, "nodata"

    # Reference value: interpolate at ref_depth (clipped to profile range).
    if ref_depth < prof["depth"].iloc[0]:
        ref_val = float(prof[var].iloc[0])
    else:
        ref_val = float(np.interp(ref_depth, prof["depth"].to_numpy(), prof[var].to_numpy()))

    diffs = np.abs(below_ref[var].to_numpy() - ref_val)
    idx = np.where(diffs >= thresh)[0]
    if len(idx) == 0:
        return np.nan, "nocrit"

    k = int(idx[0])
    if k == 0:
        return float(below_ref["depth"].iloc[0]), "atmin"

    z1 = float(below_ref["depth"].iloc[k - 1])
    z2 = float(below_ref["depth"].iloc[k])
    d1 = float(diffs[k - 1])
    d2 = float(diffs[k])
    if d2 == d1:
        return z2, "ok"
    mld = z1 + (thresh - d1) * (z2 - z1) / (d2 - d1)
    return float(mld), "ok"
