import numpy as np
import pytest

from src.sigma_to_z import sigma_to_z_vtransform2


def test_surface_and_bottom_sanity():
    # Flat bottom 100 m, 2 time steps, 4 sigma levels, 3x3 grid.
    h = np.full((3, 3), 100.0)
    zeta = np.zeros((2, 3, 3))
    # s_rho from -1 (surface) to near 0 (bottom). Use an even spacing.
    s_rho = np.array([-0.875, -0.625, -0.375, -0.125])
    Cs_r  = s_rho.copy()  # linear stretch
    hc = 10.0
    z = sigma_to_z_vtransform2(h, zeta, s_rho, Cs_r, hc)
    assert z.shape == (2, 4, 3, 3)
    # At the center cell, zeta=0 so z = h * S with S negative.
    # k=-1 (most surface) should have z ~ -100 * (-0.125) * (h/h+hc) ~ -11.4 m  (NOT surface).
    # Actually Vtransform=2: S = (hc*s + h*Cs)/(hc+h). s=-0.125, Cs=-0.125 → S = -0.125.
    # z = 0 + (0 + 100) * -0.125 = -12.5 m (the shallowest sigma level)
    assert abs(z[0, -1, 1, 1] - (-12.5)) < 1e-6
    # Deepest (k=0): s=-0.875, Cs=-0.875 → S=-0.875 → z=-87.5 (not full bottom)
    assert abs(z[0, 0, 1, 1] - (-87.5)) < 1e-6


def test_surface_elevation_offset():
    h = np.full((1, 1), 50.0)
    zeta = np.array([[[1.5]]])  # 1.5 m surface elevation
    s_rho = np.array([-1.0, 0.0])
    Cs_r = np.array([-1.0, 0.0])
    hc = 5.0
    z = sigma_to_z_vtransform2(h, zeta, s_rho, Cs_r, hc)
    # k=-1 (s=0, Cs=0): S=0, z = zeta = 1.5
    assert abs(z[0, -1, 0, 0] - 1.5) < 1e-9
    # k=0 (s=-1, Cs=-1): S = (5*-1 + 50*-1)/(5+50) = -55/55 = -1
    # z = 1.5 + (1.5 + 50) * -1 = 1.5 - 51.5 = -50 (bottom)
    assert abs(z[0, 0, 0, 0] - (-50.0)) < 1e-9


def test_rejects_bad_shapes():
    with pytest.raises(ValueError):
        sigma_to_z_vtransform2(
            h=np.zeros(5),                     # must be 2-D
            zeta=np.zeros((1, 3, 3)),
            s_rho=np.array([-1.0, 0.0]),
            Cs_r=np.array([-1.0, 0.0]),
            hc=5.0,
        )
    with pytest.raises(ValueError):
        sigma_to_z_vtransform2(
            h=np.zeros((3, 3)),
            zeta=np.zeros((3, 3)),              # must be 3-D
            s_rho=np.array([-1.0, 0.0]),
            Cs_r=np.array([-1.0, 0.0]),
            hc=5.0,
        )
    with pytest.raises(ValueError):
        sigma_to_z_vtransform2(
            h=np.zeros((3, 3)),
            zeta=np.zeros((1, 3, 3)),
            s_rho=np.array([-1.0, 0.0]),
            Cs_r=np.array([-1.0, 0.0, 1.0]),    # mismatched length
            hc=5.0,
        )
