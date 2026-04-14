"""ROMS sigma-coordinate to z conversion (Vtransform = 2).

Used by notebook 02 (`02_qc_and_align.ipynb`) and notebook 04.
"""
from __future__ import annotations

import numpy as np

__all__ = ["sigma_to_z_vtransform2"]


def sigma_to_z_vtransform2(
    h: np.ndarray,
    zeta: np.ndarray,
    s_rho: np.ndarray,
    Cs_r: np.ndarray,
    hc: float,
) -> np.ndarray:
    """Convert ROMS sigma layers to z (positive up, m), Vtransform = 2.

    z(t,k,j,i) = zeta(t,j,i) + (zeta(t,j,i) + h(j,i)) * S(k,j,i)
    S(k,j,i)   = (hc * s_rho(k) + h(j,i) * Cs_r(k)) / (hc + h(j,i))

    Parameters
    ----------
    h : (eta, xi) bathymetric depth (m, positive down).
    zeta : (t, eta, xi) free-surface elevation (m).
    s_rho : (s_rho,) sigma coordinate at rho-points, typically in [-1, 0].
    Cs_r : (s_rho,) vertical stretching function at rho-points.
    hc : scalar critical depth.

    Returns
    -------
    z : (t, s_rho, eta, xi) depth positive up (z=0 surface).
    """
    h = np.asarray(h)
    zeta = np.asarray(zeta)
    s_rho = np.asarray(s_rho)
    Cs_r = np.asarray(Cs_r)
    if h.ndim != 2:
        raise ValueError(f"h must be 2-D (eta, xi); got shape {h.shape}")
    if zeta.ndim != 3:
        raise ValueError(f"zeta must be 3-D (t, eta, xi); got shape {zeta.shape}")
    if s_rho.shape != Cs_r.shape or s_rho.ndim != 1:
        raise ValueError("s_rho and Cs_r must be matching 1-D arrays")

    h_b = h[None, None, :, :]                 # (1, 1, eta, xi)
    zeta_b = zeta[:, None, :, :]              # (t, 1, eta, xi)
    s_b = s_rho[None, :, None, None]          # (1, s_rho, 1, 1)
    C_b = Cs_r[None, :, None, None]           # (1, s_rho, 1, 1)

    S = (hc * s_b + h_b * C_b) / (hc + h_b)   # (1, s_rho, eta, xi)
    z = zeta_b + (zeta_b + h_b) * S           # (t, s_rho, eta, xi)
    return z
