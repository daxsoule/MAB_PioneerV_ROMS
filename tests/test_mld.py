import numpy as np
import pandas as pd
import pytest

from src.mld import mld_threshold


def _profile(depths, vals, var="sigma_theta"):
    return pd.DataFrame({"depth": depths, var: vals})


def test_ok_density_threshold_midcolumn():
    # Uniform above 30 m, then density jumps by 0.05 at 35 m.
    depths = np.array([25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45])
    sig    = np.array([23.0, 23.00, 23.00, 23.00, 23.00, 23.05, 23.06, 23.07, 23.07, 23.08, 23.09])
    mld, code = mld_threshold(_profile(depths, sig), "sigma_theta", 0.03, ref_depth=25.0)
    assert code == "ok"
    # Interpolated crossing between 33 m (|d|=0.00) and 35 m (|d|=0.05):
    # 33 + (0.03 - 0) * (35-33) / (0.05 - 0) = 34.2 m
    assert 34.0 < mld < 34.5


def test_atmin_when_ref_depth_above_shallowest_sample_and_gradient_is_steep():
    # Profile starts at 15 m; ref_depth=20 m. ref_val is interpolated at 20 m.
    # below_ref[0] is at 25 m, and its value already differs from ref_val by >= thresh.
    # -> code 'atmin' (MLD is somewhere in 15-25 m, unobservable from this profile).
    depths = np.array([15, 25, 30, 35])
    sig    = np.array([23.0, 23.10, 23.12, 23.14])  # 0.10 jump at 25 m vs 23.0 at 15 m
    mld, code = mld_threshold(_profile(depths, sig), "sigma_theta", 0.03, ref_depth=20.0)
    assert code == "atmin"
    assert mld == 25.0


def test_nocrit_when_threshold_never_reached():
    depths = np.array([25, 30, 35, 40, 45])
    sig    = np.array([23.00, 23.005, 23.010, 23.015, 23.020])
    mld, code = mld_threshold(_profile(depths, sig), "sigma_theta", 0.03, ref_depth=25.0)
    assert code == "nocrit"
    assert np.isnan(mld)


def test_nodata_when_too_few_samples():
    depths = np.array([25, 30])
    sig    = np.array([23.00, 23.05])
    mld, code = mld_threshold(_profile(depths, sig), "sigma_theta", 0.03, ref_depth=25.0)
    assert code == "nodata"
    assert np.isnan(mld)


def test_works_on_temperature_column():
    depths = np.array([25, 28, 31, 34, 37, 40])
    T      = np.array([22.0, 22.0, 22.0, 21.5, 18.0, 15.0])
    mld, code = mld_threshold(_profile(depths, T, var="T"), "T", 0.2, ref_depth=25.0)
    assert code == "ok"
    # Threshold reached between 31 (|d|=0) and 34 (|d|=0.5): 31+(0.2/0.5)*3=32.2
    assert 32.0 < mld < 32.5


def test_ignores_nan_in_variable():
    depths = np.array([25, 27, 29, 31, 33, 35])
    sig    = np.array([23.0, np.nan, 23.00, np.nan, 23.00, 23.10])
    mld, code = mld_threshold(_profile(depths, sig), "sigma_theta", 0.03, ref_depth=25.0)
    # NaNs dropped; remaining 4 points; crossing between 33 (d=0) and 35 (d=0.1)
    assert code == "ok"
    assert 33.5 < mld < 34.1


def test_ref_depth_above_shallowest_samples_used():
    # ref_depth is shallower than the first sample; use first-sample value as ref.
    depths = np.array([25, 30, 35, 40])
    sig    = np.array([23.0, 23.05, 23.10, 23.15])
    mld, code = mld_threshold(_profile(depths, sig), "sigma_theta", 0.03, ref_depth=10.0)
    # ref_val = 23.0 (first sample), crossing at d>=0.03
    # at 25: |23.0-23.0|=0 ; at 30: |23.05-23.0|=0.05 -> crossing in (25, 30)
    # Actually — 'below_ref' starts at first sample >= ref_depth=10, which is 25.
    # diff at 25 = 0 (=ref_val). k=1 since diff[1]=0.05 >= 0.03.
    # interp: 25 + (0.03-0)*(30-25)/(0.05-0) = 28.0
    assert code == "ok"
    assert 27.8 < mld < 28.2
