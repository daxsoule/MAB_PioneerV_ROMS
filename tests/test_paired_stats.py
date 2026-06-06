import numpy as np
import pandas as pd

from src.paired_stats import paired_stats


def _hourly(start, n, values):
    t = pd.date_range(start, periods=n, freq="h")
    return pd.DataFrame({"time": t, "T": values})


def test_identical_series_r_one_bias_zero():
    obs = _hourly("2025-01-01", 24, np.linspace(10, 15, 24))
    mod = _hourly("2025-01-01", 24, np.linspace(10, 15, 24))
    out = paired_stats(obs, mod, "T",
                      pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02"),
                      "T", "day0")
    assert out["N"] == 24
    assert abs(out["bias"]) < 1e-12
    assert abs(out["rmse"]) < 1e-12
    assert abs(out["r"] - 1.0) < 1e-12


def test_constant_offset_bias_rmse():
    obs = _hourly("2025-01-01", 12, np.ones(12) * 10.0)
    mod = _hourly("2025-01-01", 12, np.ones(12) * 10.5)
    out = paired_stats(obs, mod, "T",
                      pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02"),
                      "T", "day0")
    assert out["N"] == 12
    assert abs(out["bias"] - 0.5) < 1e-12
    assert abs(out["rmse"] - 0.5) < 1e-12
    # r undefined for constant series -> np.corrcoef returns NaN; numpy raises
    # RuntimeWarning but doesn't throw; we just check NaN.
    assert np.isnan(out["r"])


def test_nan_dropped_before_stats():
    obs = pd.DataFrame({"time": pd.date_range("2025-01-01", periods=4, freq="h"),
                        "T": [10.0, np.nan, 11.0, 12.0]})
    mod = pd.DataFrame({"time": pd.date_range("2025-01-01", periods=4, freq="h"),
                        "T": [10.1, 11.0, np.nan, 12.2]})
    out = paired_stats(obs, mod, "T",
                      pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02"),
                      "T", "w")
    assert out["N"] == 2   # samples 1 and 3 survive


def test_returns_nan_when_sample_too_small():
    obs = _hourly("2025-01-01", 1, [10.0])
    mod = _hourly("2025-01-01", 1, [10.1])
    out = paired_stats(obs, mod, "T",
                      pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02"),
                      "T", "tiny")
    assert out["N"] == 1
    assert np.isnan(out["bias"])
    assert np.isnan(out["rmse"])
    assert np.isnan(out["r"])


def test_subwindow_filter():
    obs = _hourly("2025-01-01", 48, np.arange(48).astype(float))
    mod = _hourly("2025-01-01", 48, np.arange(48).astype(float) + 0.1)
    out = paired_stats(obs, mod, "T",
                      pd.Timestamp("2025-01-01 06:00"),
                      pd.Timestamp("2025-01-01 12:00"),
                      "T", "morning6h")
    assert out["N"] == 6
    assert abs(out["bias"] - 0.1) < 1e-12
