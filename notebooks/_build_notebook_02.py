"""Build notebooks/02_qc_and_align.ipynb from cell definitions.

Run with:  uv run python notebooks/_build_notebook_02.py

Purpose: Phase 3 of spec 001. Read raw files produced by notebook 01,
apply QC, convert DOPPIO sigma->z, put everything on a common
hourly x depth grid, and write tidy Parquet to outputs/data/processed/.
"""

from pathlib import Path

import nbformat as nbf

DISCLOSURE = (
    "*AI-generated draft (Claude, Anthropic) — for review. All parameters and "
    "data paths are derived from version-controlled scripts and data. The prose "
    "content of this notebook is AI-drafted; review for accuracy before external "
    "sharing.*"
)


def md(body: str, with_disclosure: bool = False) -> nbf.NotebookNode:
    if with_disclosure:
        text = (
            f"{DISCLOSURE}\n\n"
            f"<span style=\"font-family: 'Courier New', monospace;\">\n\n"
            f"{body}\n\n"
            f"</span>"
        )
    else:
        text = (
            f"<span style=\"font-family: 'Courier New', monospace;\">\n\n"
            f"{body}\n\n"
            f"</span>"
        )
    return nbf.v4.new_markdown_cell(text)


def code(body: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(body)


cells = []

# ---- Title ----------------------------------------------------------------
cells.append(
    md(
        """# Spec 001 — Notebook 02: QC & align (Phase 3)

Inputs (from notebook 01, under `outputs/data/raw/`):

- `CP13NOPM-WFP01-03-CTDPFK000_erin.nc` — WFP profiler, 25–79 m
- `CP13NOPM-SBI01-02-CTDMOS011_erin.nc` — near-surface CTD, ~0.5 m
- `doppio_CP13N_erin.nc` — DOPPIO operational slice, 337 hourly × 40 sigma

This notebook:

1. Loads both obs streams; applies OOI QARTOD filter (accept flag 1 or 2)
   and the constitution's range checks (T: 2–28 °C, S: 28–37 PSU,
   P: 0–500 dbar). Storm-window excursions are **flagged for review**,
   not silently rejected, per constitution.
2. Audits depth coverage of the WFP deployment across the event window.
3. Converts DOPPIO sigma coordinates to z using the ROMS Vtransform=2
   formula with `hc`, `Cs_r`, `h`, `zeta`.
4. Extracts the DOPPIO column nearest CP13N and regrids it onto a
   common depth grid matching the WFP's usable range.
5. Aligns all three products (WFP, SBI, DOPPIO) onto a common hourly
   cadence by averaging (do not upsample).
6. Writes tidy Parquet outputs to `outputs/data/processed/`.""",
        with_disclosure=True,
    )
)

# ---- Install --------------------------------------------------------------
cells.append(md("## 1. Install dependencies"))
cells.append(
    code(
        """%pip install --quiet \\
    'xarray>=2024.1.0' \\
    'netCDF4>=1.6.5' \\
    'numpy>=1.24' \\
    'pandas>=2.0' \\
    'pyarrow>=15.0' \\
    'plotly>=5.20' \\
    'gsw>=3.6'
"""
    )
)

# ---- Constants ------------------------------------------------------------
cells.append(md("## 2. Constants and paths"))
cells.append(
    code(
        """import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

warnings.filterwarnings('ignore', category=FutureWarning)

# Paths (relative to notebooks/)
RAW_DIR  = Path('../outputs/data/raw')
PROC_DIR = Path('../outputs/data/processed')
PROC_DIR.mkdir(parents=True, exist_ok=True)

WFP_IN    = RAW_DIR / 'CP13NOPM-WFP01-03-CTDPFK000_erin.nc'
SBI_IN    = RAW_DIR / 'CP13NOPM-SBI01-02-CTDMOS011_erin.nc'
DOPPIO_IN = RAW_DIR / 'doppio_CP13N_erin.nc'

WFP_OUT    = PROC_DIR / 'obs_profile_CP13N_erin.parquet'      # WFP gridded
SBI_OUT    = PROC_DIR / 'obs_surface_CP13N_erin.parquet'      # SBI time series
DOPPIO_OUT = PROC_DIR / 'doppio_profile_CP13N_erin.parquet'   # DOPPIO gridded

# Event window + CPA (tz-naive UTC, same convention as notebook 01)
EVENT_START = pd.Timestamp('2025-08-15')
EVENT_END   = pd.Timestamp('2025-08-29')
CPA_TIME    = pd.Timestamp('2025-08-21 12:00')

# Constitution QC bounds
T_MIN, T_MAX = 2.0, 28.0      # °C
S_MIN, S_MAX = 28.0, 37.0     # PSU
P_MIN, P_MAX = 0.0, 500.0     # dbar
QARTOD_GOOD  = (1, 2)         # 1=pass, 2=not_evaluated

# Storm sub-window (for excursion review, per constitution)
STORM_START = pd.Timestamp('2025-08-20')
STORM_END   = pd.Timestamp('2025-08-22')

# Common grids
TIME_CADENCE = '1h'             # hourly
DEPTH_BIN_M  = 2.0              # 2 m depth bins for WFP gridding
"""
    )
)

# ---- Step 3: WFP QARTOD + range ------------------------------------------
cells.append(
    md(
        """## 3. WFP: QARTOD + range filter (T021–T022)

Keep samples where both T and S QARTOD flags are 1 (pass) or 2
(not evaluated). Apply the constitution's MAB shelf/slope range
bounds. For samples flagged by a range check **during the storm
sub-window**, do not silently reject — collect them for a review
table that the user can inspect."""
    )
)
cells.append(
    code(
        """wfp_ds = xr.open_dataset(WFP_IN)
wfp = pd.DataFrame({
    'time':       pd.to_datetime(wfp_ds.time.values),
    'depth':      wfp_ds.depth.values,
    'pressure':   wfp_ds.sea_water_pressure.values,
    'T':          wfp_ds.sea_water_temperature.values,
    'S':          wfp_ds.sea_water_practical_salinity.values,
    't_qartod':   wfp_ds.sea_water_temperature_qartod_results.values.astype('int8'),
    's_qartod':   wfp_ds.sea_water_practical_salinity_qartod_results.values.astype('int8'),
})
wfp_ds.close()

n0 = len(wfp)
# QARTOD filter
qc_t = wfp['t_qartod'].isin(QARTOD_GOOD)
qc_s = wfp['s_qartod'].isin(QARTOD_GOOD)
wfp.loc[~qc_t, 'T'] = np.nan
wfp.loc[~qc_s, 'S'] = np.nan

# Range filter (constitution bounds). Track excursions separately.
storm_mask = (wfp['time'] >= STORM_START) & (wfp['time'] < STORM_END)
t_out = (wfp['T'] < T_MIN) | (wfp['T'] > T_MAX)
s_out = (wfp['S'] < S_MIN) | (wfp['S'] > S_MAX)
p_out = (wfp['pressure'] < P_MIN) | (wfp['pressure'] > P_MAX)

storm_excursions = wfp.loc[storm_mask & (t_out | s_out | p_out)].copy()

# Apply range-filter: set out-of-range values to NaN (flag preserved elsewhere)
wfp.loc[t_out, 'T'] = np.nan
wfp.loc[s_out, 'S'] = np.nan
wfp.loc[p_out, 'pressure'] = np.nan

print(f'=== WFP QC summary ===')
print(f'  samples in:                 {n0:,}')
print(f'  QARTOD rejections (T):      {int((~qc_t).sum()):,}')
print(f'  QARTOD rejections (S):      {int((~qc_s).sum()):,}')
print(f'  Range rejections (T):       {int(t_out.sum()):,}  (min {wfp["T"].min():.2f}, max {wfp["T"].max():.2f} after)')
print(f'  Range rejections (S):       {int(s_out.sum()):,}  (min {wfp["S"].min():.2f}, max {wfp["S"].max():.2f} after)')
print(f'  Range rejections (P):       {int(p_out.sum()):,}')
print(f'  Storm-window excursions to review: {len(storm_excursions):,}')
"""
    )
)

# ---- Step 4: WFP depth audit ---------------------------------------------
cells.append(
    md(
        """## 4. WFP depth coverage audit (T023)

Tabulate depth statistics across the event window. Confirm usable range.
If max depth is shallower than expected, note and halt before downstream
stages."""
    )
)
cells.append(
    code(
        """# Depth stats on the cleaned (non-NaN T) subset
wfp_valid = wfp.dropna(subset=['T']).copy()

print('=== WFP depth coverage across event window ===')
print(f'  samples (valid T): {len(wfp_valid):,}')
print(f'  min depth:         {wfp_valid.depth.min():.2f} m')
print(f'  1st %ile:          {wfp_valid.depth.quantile(0.01):.2f} m')
print(f'  median:            {wfp_valid.depth.median():.2f} m')
print(f'  99th %ile:         {wfp_valid.depth.quantile(0.99):.2f} m')
print(f'  max depth:         {wfp_valid.depth.max():.2f} m')

# Depth vs time — coarse tabulation
wfp_valid['day'] = wfp_valid.time.dt.floor('D')
daily_depth = wfp_valid.groupby('day').agg(
    n=('depth', 'count'),
    z_min=('depth', 'min'),
    z_p50=('depth', 'median'),
    z_max=('depth', 'max'),
).round(2)
print('\\nDaily depth coverage (WFP):')
print(daily_depth.to_string())

# Usable range: choose conservatively
USABLE_Z_MIN = max(24.0, wfp_valid.depth.quantile(0.01))
USABLE_Z_MAX = min(80.0, wfp_valid.depth.quantile(0.99))
print(f'\\nUsable depth range for common grid: {USABLE_Z_MIN:.1f} → {USABLE_Z_MAX:.1f} m')
assert USABLE_Z_MAX > USABLE_Z_MIN, 'Usable range collapsed — audit failed.'
"""
    )
)

# ---- Step 5: WFP to common time x depth grid -----------------------------
cells.append(
    md(
        """## 5. Regrid WFP to common (time × depth) grid (T024)

Bin into hourly time × 2 m depth cells, taking the mean within each
cell. Produces a tidy long table with columns `time`, `depth`, `T`,
`S`, `pressure`, `n_samples`."""
    )
)
cells.append(
    code(
        """# Build depth grid
depth_centers = np.arange(
    np.floor(USABLE_Z_MIN / DEPTH_BIN_M) * DEPTH_BIN_M + DEPTH_BIN_M / 2,
    np.ceil(USABLE_Z_MAX / DEPTH_BIN_M) * DEPTH_BIN_M,
    DEPTH_BIN_M,
)
print(f'Depth bin centers: {depth_centers[0]:.1f} → {depth_centers[-1]:.1f} m  ({len(depth_centers)} bins of {DEPTH_BIN_M:.1f} m)')

# Assign bins
wfp_valid['depth_bin'] = np.round((wfp_valid.depth - DEPTH_BIN_M / 2) / DEPTH_BIN_M) * DEPTH_BIN_M + DEPTH_BIN_M / 2
# Restrict to usable range
wfp_valid = wfp_valid[
    (wfp_valid.depth_bin >= depth_centers[0]) & (wfp_valid.depth_bin <= depth_centers[-1])
]

# Hourly floor for time binning
wfp_valid['time_bin'] = wfp_valid.time.dt.floor(TIME_CADENCE)

# Group: mean within each (time_bin, depth_bin) cell
wfp_grid = (
    wfp_valid
    .groupby(['time_bin', 'depth_bin'], as_index=False)
    .agg(
        T=('T', 'mean'),
        S=('S', 'mean'),
        pressure=('pressure', 'mean'),
        n_samples=('T', 'count'),
    )
    .rename(columns={'time_bin': 'time', 'depth_bin': 'depth'})
)
wfp_grid['source'] = 'wfp'

print(f'\\nWFP gridded: {len(wfp_grid):,} cells')
print(f'  unique times:  {wfp_grid.time.nunique()}')
print(f'  unique depths: {wfp_grid.depth.nunique()}')
print(f'  fill rate:     {100 * len(wfp_grid) / (wfp_grid.time.nunique() * wfp_grid.depth.nunique()):.1f}%')

wfp_grid.to_parquet(WFP_OUT, index=False)
print(f'\\nWrote: {WFP_OUT}  ({WFP_OUT.stat().st_size / 1e6:.2f} MB)')
"""
    )
)

# ---- Step 6: SBI surface time series -------------------------------------
cells.append(
    md(
        """## 6. SBI: QC + hourly time series

SBI01 is a single-depth cable-mounted CTD (~0.5 m). Same QC pipeline,
then resample to hourly. No depth grid — it's a surface time series."""
    )
)
cells.append(
    code(
        """sbi_ds = xr.open_dataset(SBI_IN)
sbi = pd.DataFrame({
    'time':     pd.to_datetime(sbi_ds.time.values),
    'depth':    sbi_ds.depth.values,
    'T':        sbi_ds.sea_water_temperature.values,
    'S':        sbi_ds.sea_water_practical_salinity.values,
    'pressure': sbi_ds.sea_water_pressure.values,
    't_qartod': sbi_ds.sea_water_temperature_qartod_results.values.astype('int8'),
    's_qartod': sbi_ds.sea_water_practical_salinity_qartod_results.values.astype('int8'),
})
sbi_ds.close()

n0 = len(sbi)
sbi.loc[~sbi['t_qartod'].isin(QARTOD_GOOD), 'T'] = np.nan
sbi.loc[~sbi['s_qartod'].isin(QARTOD_GOOD), 'S'] = np.nan
# Use sbi['T'] (NOT sbi.T — which is DataFrame transpose).
sbi.loc[(sbi['T'] < T_MIN) | (sbi['T'] > T_MAX), 'T'] = np.nan
sbi.loc[(sbi['S'] < S_MIN) | (sbi['S'] > S_MAX), 'S'] = np.nan

sbi['time_bin'] = sbi['time'].dt.floor(TIME_CADENCE)
sbi_grid = (
    sbi.groupby('time_bin', as_index=False)
    .agg(
        T=('T', 'mean'),
        S=('S', 'mean'),
        pressure=('pressure', 'mean'),
        depth=('depth', 'mean'),
        n_samples=('T', 'count'),
    )
    .rename(columns={'time_bin': 'time'})
)
sbi_grid['source'] = 'sbi'

print(f'SBI: {n0:,} raw samples -> {len(sbi_grid):,} hourly bins')
print(f'  depth (mean across time bins): {sbi_grid.depth.mean():.2f} m')
print(f'  T range: {sbi_grid["T"].min():.2f} → {sbi_grid["T"].max():.2f} °C')
print(f'  S range: {sbi_grid["S"].min():.2f} → {sbi_grid["S"].max():.2f} PSU')

sbi_grid.to_parquet(SBI_OUT, index=False)
print(f'\\nWrote: {SBI_OUT}  ({SBI_OUT.stat().st_size / 1e6:.2f} MB)')
"""
    )
)

# ---- Step 7: DOPPIO sigma -> z -------------------------------------------
cells.append(
    md(
        """## 7. DOPPIO sigma → z conversion (T025)

ROMS uses a terrain-following sigma coordinate. Convert to depth (z,
positive up from sea surface) using Vtransform=2 (DOPPIO operational
standard):

    S(k,j,i) = (hc · s_rho(k) + h(j,i) · Cs_r(k)) / (hc + h(j,i))
    z(t,k,j,i) = zeta(t,j,i) + (zeta(t,j,i) + h(j,i)) · S(k,j,i)

For the comparison, we need depth in positive-down meters to match
the obs convention. The notebook below reports `z_pos_down = -z`.

Vtransform=2 is the DOPPIO 2017_da standard. The sanity check at the
end of this section verifies the conversion: `z` at the surface-most
sigma level (k=-1) should be ≈ `zeta` (surface), and at the deepest
sigma level (k=0) should be ≈ `-h` (bottom). If Rutgers ever changes
to Vtransform=1 the formula needs swapping — the sanity check will
fail loudly."""
    )
)
cells.append(
    code(
        """doppio = xr.open_dataset(DOPPIO_IN)
print(f'DOPPIO dims: {dict(doppio.sizes)}')

# s_rho in ROMS runs from -1 (surface) to near 0 (bottom) — convention reversed
# from some documentation. Let's print the s_rho values to confirm.
s_rho = doppio.s_rho.values
Cs_r  = doppio.Cs_r.values
hc    = float(doppio.hc.values)
print(f's_rho: {s_rho[0]:.4f} (k=0) → {s_rho[-1]:.4f} (k=-1),  count={len(s_rho)}')
print(f'Cs_r:  {Cs_r[0]:.4f} → {Cs_r[-1]:.4f}')
print(f'hc:    {hc:.2f}')
"""
    )
)
cells.append(
    code(
        """# Compute z for every (time, k, j, i)
# Vtransform=2
h    = doppio.h.values                             # (eta, xi)
zeta = doppio.zeta.values                          # (time, eta, xi)

# Broadcast shapes: we want z of shape (time, s_rho, eta, xi)
h_b    = h[None, None, :, :]                       # (1, 1, eta, xi)
zeta_b = zeta[:, None, :, :]                       # (time, 1, eta, xi)
s_b    = s_rho[None, :, None, None]                # (1, s_rho, 1, 1)
C_b    = Cs_r[None, :, None, None]                 # (1, s_rho, 1, 1)

S = (hc * s_b + h_b * C_b) / (hc + h_b)            # (1, s_rho, eta, xi)
z = zeta_b + (zeta_b + h_b) * S                    # (time, s_rho, eta, xi)

# z convention: positive up (z=0 at surface, z<0 below). Convert to
# positive-down depth to match obs.
z_down = -z

# Sanity checks
# At the center (eta=3, xi=3), k=-1 should be near surface (~ zeta),
# k=0 should be near -h (bottom).
print('Center cell (eta=3, xi=3), t=0:')
print(f'  h          = {h[3, 3]:.2f} m')
print(f'  zeta(t=0)  = {zeta[0, 3, 3]:.4f} m')
print(f'  z(k=0)     = {z[0, 0, 3, 3]:.2f} m  (should be near -h)')
print(f'  z(k=-1)    = {z[0, -1, 3, 3]:.4f} m  (should be near zeta)')
print(f'  z_down(k=0)  = {z_down[0, 0, 3, 3]:.2f} m')
print(f'  z_down(k=-1) = {z_down[0, -1, 3, 3]:.4f} m')

# Attach z_down as a coordinate on the dataset for convenience
doppio = doppio.assign_coords(z_down=(('time', 's_rho', 'eta_rho', 'xi_rho'), z_down))
print('\\nz_down coordinate attached.')
"""
    )
)

# ---- Step 8: DOPPIO nearest-rho column to common depth grid -------------
cells.append(
    md(
        """## 8. Extract DOPPIO nearest-rho column; regrid to common depth grid (T026)

Center of the 7×7 buffer is the nearest rho-point from notebook 01.
Take that column, interpolate T/S onto the common depth grid
(matching the WFP grid)."""
    )
)
cells.append(
    code(
        """# Center rho-point of the ±3 buffer is at index 3 in each horizontal dim
eta_c, xi_c = 3, 3
col = doppio.isel(eta_rho=eta_c, xi_rho=xi_c)
print(f'Column h at center: {float(col.h.values):.2f} m')

# Per-time interpolation of (z_down(k), T(k)) and (z_down(k), S(k)) onto
# depth_centers. ROMS sigma: for a given time, z_down(k) is a 1D profile
# through k. Use numpy.interp per time.

doppio_rows = []
times = pd.to_datetime(col.time.values)
for t_idx, t in enumerate(times):
    z_prof = col.z_down.isel(time=t_idx).values        # (s_rho,)
    t_prof = col.temp.isel(time=t_idx).values          # (s_rho,)
    s_prof = col.salt.isel(time=t_idx).values          # (s_rho,)

    # Sort by z ascending for np.interp (needs monotonic x)
    order = np.argsort(z_prof)
    z_s   = z_prof[order]
    t_s   = t_prof[order]
    s_s   = s_prof[order]

    # Interpolate only within the column's actual depth range
    valid = (depth_centers >= z_s[0]) & (depth_centers <= z_s[-1])
    T_i = np.full_like(depth_centers, np.nan, dtype=float)
    S_i = np.full_like(depth_centers, np.nan, dtype=float)
    T_i[valid] = np.interp(depth_centers[valid], z_s, t_s)
    S_i[valid] = np.interp(depth_centers[valid], z_s, s_s)

    for z_c, T_v, S_v in zip(depth_centers, T_i, S_i):
        doppio_rows.append({'time': t, 'depth': float(z_c), 'T': float(T_v), 'S': float(S_v)})

doppio_grid = pd.DataFrame(doppio_rows)
doppio_grid['source'] = 'doppio'
print(f'DOPPIO gridded: {len(doppio_grid):,} cells')
print(f'  unique times:  {doppio_grid.time.nunique()}')
print(f'  unique depths: {doppio_grid.depth.nunique()}')
print(f'  T range: {doppio_grid["T"].min():.2f} → {doppio_grid["T"].max():.2f} °C')
print(f'  S range: {doppio_grid["S"].min():.2f} → {doppio_grid["S"].max():.2f} PSU')

# Already hourly from the source (OPeNDAP 2017_da History_Best is hourly),
# but floor to ensure perfect alignment with obs hourly bins.
doppio_grid['time'] = doppio_grid['time'].dt.floor(TIME_CADENCE)
doppio_grid.to_parquet(DOPPIO_OUT, index=False)
print(f'\\nWrote: {DOPPIO_OUT}  ({DOPPIO_OUT.stat().st_size / 1e6:.2f} MB)')
"""
    )
)

# ---- Step 9: QC matching ----------------------------------------------
cells.append(
    md(
        """## 9. QC — matching time and depth grids (T029)"""
    )
)
cells.append(
    code(
        """# Load each, check time/depth alignment.
wfp_g    = pd.read_parquet(WFP_OUT)
doppio_g = pd.read_parquet(DOPPIO_OUT)

wfp_t    = set(wfp_g.time.dt.to_pydatetime())
doppio_t = set(doppio_g.time.dt.to_pydatetime())

wfp_z    = set(wfp_g.depth.round(2))
doppio_z = set(doppio_g.depth.round(2))

print('=== WFP vs DOPPIO alignment check ===')
print(f'  times in WFP:     {len(wfp_t)}')
print(f'  times in DOPPIO:  {len(doppio_t)}')
print(f'  intersection:     {len(wfp_t & doppio_t)}')
print(f'  only in WFP:      {len(wfp_t - doppio_t)}')
print(f'  only in DOPPIO:   {len(doppio_t - wfp_t)}')

print(f'\\n  depths in WFP:     {len(wfp_z)}')
print(f'  depths in DOPPIO:  {len(doppio_z)}')
print(f'  intersection:      {len(wfp_z & doppio_z)}')

# Fill rate over common grid
common_t = sorted(wfp_t & doppio_t)
common_z = sorted(wfp_z & doppio_z)
wfp_common    = wfp_g[wfp_g.time.isin(common_t)    & wfp_g.depth.round(2).isin(common_z)]
doppio_common = doppio_g[doppio_g.time.isin(common_t) & doppio_g.depth.round(2).isin(common_z)]
print(f'\\n  WFP cells on common grid:    {len(wfp_common):,}')
print(f'  DOPPIO cells on common grid: {len(doppio_common):,}')
"""
    )
)

# ---- Step 10: quick-look plot -------------------------------------------
cells.append(
    md(
        """## 10. Quick-look comparison (T030)

Not the final Hovmöller figure — just a sanity check that both
products produce sensible T(z, t) fields on the common grid."""
    )
)
cells.append(
    code(
        """import plotly.graph_objects as go
from plotly.subplots import make_subplots

wfp_pv    = wfp_g.pivot(index='depth', columns='time', values='T').sort_index()
doppio_pv = doppio_g.pivot(index='depth', columns='time', values='T').sort_index()

# Common color scale — take min/max of each separately
tmin = float(min(np.nanmin(wfp_pv.values), np.nanmin(doppio_pv.values)))
tmax = float(max(np.nanmax(wfp_pv.values), np.nanmax(doppio_pv.values)))

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('WFP obs T(z, t)', 'DOPPIO T(z, t)'),
    shared_yaxes=True,
    horizontal_spacing=0.08,
)
fig.add_trace(
    go.Heatmap(x=wfp_pv.columns, y=wfp_pv.index, z=wfp_pv.values,
               zmin=tmin, zmax=tmax, colorscale='RdYlBu_r',
               colorbar=dict(title='T (°C)', x=1.02)),
    row=1, col=1,
)
fig.add_trace(
    go.Heatmap(x=doppio_pv.columns, y=doppio_pv.index, z=doppio_pv.values,
               zmin=tmin, zmax=tmax, colorscale='RdYlBu_r', showscale=False),
    row=1, col=2,
)

# CPA vertical line
for c in (1, 2):
    fig.add_vline(x=CPA_TIME, line=dict(color='black', width=1, dash='dash'), row=1, col=c)

fig.update_yaxes(autorange='reversed', title='Depth (m)', row=1, col=1)
fig.update_yaxes(autorange='reversed', row=1, col=2)
fig.update_xaxes(title='Time (UTC)', row=1, col=1)
fig.update_xaxes(title='Time (UTC)', row=1, col=2)
fig.update_layout(
    title='Quick-look — WFP vs DOPPIO temperature (Hurricane Erin window, CPA dashed)',
    height=500, width=1100, template='plotly_white',
)
fig
"""
    )
)

# ---- Summary --------------------------------------------------------------
cells.append(
    md(
        """## Summary

Outputs in `outputs/data/processed/`:

- `obs_profile_CP13N_erin.parquet` — WFP on hourly × 2 m grid (25–79 m)
- `obs_surface_CP13N_erin.parquet` — SBI hourly time series (~0.5 m)
- `doppio_profile_CP13N_erin.parquet` — DOPPIO at nearest rho-point on same grid

Next: notebook 03 — Hovmöller comparison (Figures 1–4)."""
    )
)

# ---- Build -----------------------------------------------------------
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python"},
}

out_path = Path(__file__).parent / "02_qc_and_align.ipynb"
with out_path.open("w") as f:
    nbf.write(nb, f)

print(f"Wrote {out_path}")
print(f"  cells: {len(cells)} ({sum(1 for c in cells if c.cell_type == 'markdown')} md, {sum(1 for c in cells if c.cell_type == 'code')} code)")
