"""Build notebooks/04_mixed_layer_response.ipynb from cell definitions.

Run with:  uv run python notebooks/_build_notebook_04.py

Phase 5 of spec 001: Figures 5-6 + Tables 1-2.
"""

from pathlib import Path

import nbformat as nbf

DISCLOSURE = (
    "*AI-generated draft (Claude, Anthropic) — for review. All parameters and "
    "figures are derived from version-controlled scripts and data. The prose "
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
        """# Spec 001 — Notebook 04: MLD + surface time series + comparison stats (Phase 5)

Final analysis notebook for spec 001. Produces:

- **Figure 5** — Mixed-layer depth (MLD) time series: obs (WFP) vs.
  DOPPIO, both via density threshold (Δσθ = 0.03 kg m⁻³) and
  temperature threshold (ΔT = 0.2 °C) as sensitivity check. Sub-window
  shading: pre-storm / storm / recovery.
- **Figure 6** — Surface T and S time series: SBI (~0.5 m) vs. DOPPIO
  surface (interpolated to ~0.5 m). CPA marked.
- **Table 1** — Comparison statistics (bias, RMSE, correlation) for
  surface T, surface S, and MLD per sub-window.
- **Table 2** — Data provenance.

**Important caveat** (per research.md Phase 0.2): CP13NOPM WFP only
samples 25–79 m. For the density-threshold MLD we use a **25 m
reference depth** for both obs and DOPPIO (non-standard — de Boyer
Montégut 2004 uses 10 m — but necessary for consistency given the
WFP's lower reach). When the "true" MLD is shallower than 25 m, the
reported MLD is a lower-bound artifact — those samples are flagged.""",
        with_disclosure=True,
    )
)

# ---- Install --------------------------------------------------------------
cells.append(md("## 1. Install dependencies"))
cells.append(
    code(
        """%pip install --quiet \\
    'pandas>=2.0' \\
    'numpy>=1.24' \\
    'pyarrow>=15.0' \\
    'plotly>=5.20' \\
    'gsw>=3.6'
"""
    )
)

# ---- Load data ----------------------------------------------------------
cells.append(md("## 2. Load processed data + constants"))
cells.append(
    code(
        """from pathlib import Path

import numpy as np
import pandas as pd
import gsw
import plotly.graph_objects as go
import xarray as xr
from plotly.subplots import make_subplots

PROC_DIR = Path('../outputs/data/processed')
RAW_DIR  = Path('../outputs/data/raw')
FIG_DIR  = Path('../outputs/figures/001-erin-mab-response')
TBL_DIR  = Path('../outputs/tables/001-erin-mab-response')
TBL_DIR.mkdir(parents=True, exist_ok=True)

wfp    = pd.read_parquet(PROC_DIR / 'obs_profile_CP13N_erin.parquet')
sbi    = pd.read_parquet(PROC_DIR / 'obs_surface_CP13N_erin.parquet')
doppio = pd.read_parquet(PROC_DIR / 'doppio_profile_CP13N_erin.parquet')

# Sub-windows (per spec)
PRE_START   = pd.Timestamp('2025-08-15')
PRE_END     = pd.Timestamp('2025-08-20')
STORM_START = pd.Timestamp('2025-08-20')
STORM_END   = pd.Timestamp('2025-08-22')
REC_START   = pd.Timestamp('2025-08-22')
REC_END     = pd.Timestamp('2025-08-29')
CPA_TIME    = pd.Timestamp('2025-08-21 12:00')

# MLD thresholds
DSIG_THRESH = 0.03   # kg/m^3 (de Boyer Montégut 2004)
DT_THRESH   = 0.2    # °C

# Reference depth for thresholding — constrained by WFP coverage.
# WFP starts at 25 m; we use this for BOTH products so comparisons are
# consistent. Document non-standard choice in captions.
REF_DEPTH   = 25.0   # m

print(f'wfp:    {len(wfp):,} cells, {wfp.time.nunique()} times, depth {wfp.depth.min()}-{wfp.depth.max()} m')
print(f'sbi:    {len(sbi):,} hourly bins at ~{sbi.depth.mean():.2f} m')
print(f'doppio: {len(doppio):,} cells, {doppio.time.nunique()} times, depth {doppio.depth.min()}-{doppio.depth.max()} m')
"""
    )
)

# ---- Potential density --------------------------------------------------
cells.append(md("## 3. Potential density via gsw/TEOS-10 (T039)"))
cells.append(
    code(
        """# Add a sigma_theta column to both profile frames.
# gsw needs absolute salinity and conservative temperature; convert via
# gsw.SA_from_SP(SP, p, lon, lat) then gsw.CT_from_t(SA, t, p).

# CP13N position (read from raw WFP)
_wfp_raw = xr.open_dataset(RAW_DIR / 'CP13NOPM-WFP01-03-CTDPFK000_erin.nc')
CP13N_LAT = float(_wfp_raw.lat.values.flat[0])
CP13N_LON = float(_wfp_raw.lon.values.flat[0])
_wfp_raw.close()

def add_sigma_theta(df):
    # pressure might be NaN; fall back to depth (1 dbar ≈ 1 m for shelf work)
    p = df['pressure'].fillna(df['depth']).values if 'pressure' in df else df['depth'].values
    SP = df['S'].values
    t  = df['T'].values
    SA = gsw.SA_from_SP(SP, p, CP13N_LON, CP13N_LAT)
    CT = gsw.CT_from_t(SA, t, p)
    return gsw.sigma0(SA, CT)  # potential density anomaly, kg/m^3

wfp['sigma_theta']    = add_sigma_theta(wfp)
doppio['sigma_theta'] = add_sigma_theta(doppio)

print('WFP    sigma_theta range: {:.3f} – {:.3f}'.format(
    wfp['sigma_theta'].min(), wfp['sigma_theta'].max()))
print('DOPPIO sigma_theta range: {:.3f} – {:.3f}'.format(
    doppio['sigma_theta'].min(), doppio['sigma_theta'].max()))
"""
    )
)

# ---- MLD computation ----------------------------------------------------
cells.append(
    md(
        """## 4. Mixed-layer depth per time step (T040–T041)

For each time step, extract the profile (T, S, sigma_theta over depth),
find the reference value at 25 m, and locate the first depth below the
reference where the variable differs by the threshold.

Both criteria implemented: density (Δσθ = 0.03 kg m⁻³) and temperature
(ΔT = 0.2 °C). Report both for a sensitivity check.

**Edge case**: if the threshold is not reached within the profile (MLD
extends deeper than our deepest sample), return NaN and flag. Similarly,
if the mixed layer is shallower than the 25 m reference, the returned
"MLD" is a lower bound at 25 m — flagged."""
    )
)
cells.append(
    code(
        """def mld_threshold(df_prof, var, thresh, ref_depth=REF_DEPTH):
    \"\"\"Compute MLD from a depth-sorted profile via a fixed threshold.

    Returns (mld_m, code) where code is:
      'ok'     : threshold found within profile, MLD is reliable
      'atmin'  : |var - ref| >= thresh at ref_depth already
                 (mixed layer < ref_depth; MLD is a lower bound)
      'nocrit' : threshold never reached in profile (MLD > deepest obs)
    \"\"\"
    prof = df_prof.dropna(subset=[var]).sort_values('depth').reset_index(drop=True)
    if len(prof) < 3:
        return np.nan, 'nodata'
    # Reference value: interpolate the variable at ref_depth
    if ref_depth < prof['depth'].iloc[0]:
        # reference depth is shallower than shallowest measurement
        ref_val = prof[var].iloc[0]
    else:
        ref_val = np.interp(ref_depth, prof['depth'].values, prof[var].values)
    diffs = np.abs(prof[var].values - ref_val)
    # Walk downward from the first sample at/below ref
    below_ref = prof[prof['depth'] >= ref_depth].reset_index(drop=True)
    if below_ref.empty:
        return np.nan, 'nodata'
    # Check the reference depth itself
    if below_ref[var].iloc[0] is None or np.isnan(below_ref[var].iloc[0]):
        return np.nan, 'nodata'
    # find the first index where |diff| >= thresh
    diff_below = np.abs(below_ref[var].values - ref_val)
    idx = np.where(diff_below >= thresh)[0]
    if len(idx) == 0:
        return np.nan, 'nocrit'
    k = idx[0]
    if k == 0:
        # already exceeded threshold at ref_depth — MLD is a lower bound
        return float(below_ref['depth'].iloc[0]), 'atmin'
    # linear interpolation between k-1 and k
    z1, z2 = below_ref['depth'].iloc[k-1], below_ref['depth'].iloc[k]
    d1, d2 = diff_below[k-1], diff_below[k]
    if d2 == d1:
        return float(z2), 'ok'
    mld = z1 + (thresh - d1) * (z2 - z1) / (d2 - d1)
    return float(mld), 'ok'


def compute_mld_series(df, label):
    rows = []
    for t, group in df.groupby('time'):
        m_sig, c_sig = mld_threshold(group, 'sigma_theta', DSIG_THRESH)
        m_T,   c_T   = mld_threshold(group, 'T', DT_THRESH)
        rows.append({
            'time':       t,
            'mld_sigma':  m_sig, 'code_sigma': c_sig,
            'mld_temp':   m_T,   'code_temp':  c_T,
            'source':     label,
        })
    return pd.DataFrame(rows)

mld_wfp    = compute_mld_series(wfp, 'wfp')
mld_doppio = compute_mld_series(doppio, 'doppio')

print('=== WFP MLD summary ===')
print(mld_wfp[['code_sigma', 'code_temp']].apply(pd.Series.value_counts).fillna(0).astype(int))
print(f'  MLD (density) range: {mld_wfp["mld_sigma"].min():.1f} – {mld_wfp["mld_sigma"].max():.1f} m  (median {mld_wfp["mld_sigma"].median():.1f})')
print(f'  MLD (temp)    range: {mld_wfp["mld_temp"].min():.1f} – {mld_wfp["mld_temp"].max():.1f} m  (median {mld_wfp["mld_temp"].median():.1f})')

print('\\n=== DOPPIO MLD summary ===')
print(mld_doppio[['code_sigma', 'code_temp']].apply(pd.Series.value_counts).fillna(0).astype(int))
print(f'  MLD (density) range: {mld_doppio["mld_sigma"].min():.1f} – {mld_doppio["mld_sigma"].max():.1f} m  (median {mld_doppio["mld_sigma"].median():.1f})')
print(f'  MLD (temp)    range: {mld_doppio["mld_temp"].min():.1f} – {mld_doppio["mld_temp"].max():.1f} m  (median {mld_doppio["mld_temp"].median():.1f})')
"""
    )
)

# ---- Surface time series ------------------------------------------------
cells.append(
    md(
        """## 5. Surface time series (T042)

SBI provides obs surface T/S directly. For DOPPIO we re-interpolate the
top of the column to ~0.5 m at the center rho-point (same as Figure 3
in notebook 03) so obs and model are sampled at the same nominal depth."""
    )
)
cells.append(
    code(
        """# DOPPIO surface T and S at ~0.5 m (center rho-point)
_dp = xr.open_dataset(RAW_DIR / 'doppio_CP13N_erin.nc')
h_c    = float(_dp.h.isel(eta_rho=3, xi_rho=3).values)
Cs_r   = _dp.Cs_r.values
hc_v   = float(_dp.hc.values)
s_rho  = _dp.s_rho.values
zeta_c = _dp.zeta.isel(eta_rho=3, xi_rho=3).values
temp_c = _dp.temp.isel(eta_rho=3, xi_rho=3).values  # (time, s_rho)
salt_c = _dp.salt.isel(eta_rho=3, xi_rho=3).values
S      = (hc_v * s_rho + h_c * Cs_r) / (hc_v + h_c)
z      = zeta_c[:, None] + (zeta_c[:, None] + h_c) * S[None, :]
z_down = -z

def _surf(ary2d):
    out = np.empty(z_down.shape[0])
    for i in range(z_down.shape[0]):
        order = np.argsort(z_down[i])
        out[i] = np.interp(0.5, z_down[i][order], ary2d[i][order])
    return out

dp_surface = pd.DataFrame({
    'time': pd.to_datetime(_dp.time.values).floor('h'),
    'T':    _surf(temp_c),
    'S':    _surf(salt_c),
    'source': 'doppio',
})
_dp.close()

# SBI: already hourly; rename for consistency and add source column
sbi_surface = sbi[['time', 'T', 'S']].copy()
sbi_surface['source'] = 'sbi'

print(f'SBI surface: {len(sbi_surface)} rows, T range {sbi_surface["T"].min():.2f}-{sbi_surface["T"].max():.2f}')
print(f'DOPPIO surface: {len(dp_surface)} rows, T range {dp_surface["T"].min():.2f}-{dp_surface["T"].max():.2f}')
"""
    )
)

# ---- Figure 5: MLD ------------------------------------------------------
cells.append(
    md(
        """## 6. Figure 5 — MLD time series (T044)

Obs (WFP) and DOPPIO, two criteria overlaid, sub-window shading.

**What to look for**: both products should show MLD deepening near
the CPA. If obs shows `atmin` flags (MLD at 25 m, the reference depth)
during pre-storm, that means the pre-storm mixed layer was shallower
than 25 m — unobserved, shown as a lower-bound."""
    )
)
cells.append(
    code(
        """fig5 = go.Figure()

# Sub-window shading
shades = [
    (PRE_START,   PRE_END,   'rgba(99, 110, 250, 0.08)',  'pre-storm'),
    (STORM_START, STORM_END, 'rgba(239, 85, 59, 0.15)',    'storm'),
    (REC_START,   REC_END,   'rgba(0, 204, 150, 0.08)',    'recovery'),
]
for x0, x1, c, label in shades:
    fig5.add_vrect(x0=x0, x1=x1, fillcolor=c, line_width=0,
                   annotation_text=label, annotation_position='top left',
                   annotation_font_size=10)

for src_df, color_sig, color_T, src_label in [
    (mld_wfp,    '#C0392B', '#E67E22', 'obs (WFP)'),
    (mld_doppio, '#2980B9', '#3498DB', 'DOPPIO'),
]:
    fig5.add_trace(go.Scatter(
        x=src_df['time'], y=src_df['mld_sigma'],
        mode='lines+markers',
        marker=dict(size=5),
        line=dict(color=color_sig, width=2),
        name=f'{src_label} Δσθ=0.03',
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>MLD=%{y:.1f} m<extra>'+src_label+' density</extra>',
    ))
    fig5.add_trace(go.Scatter(
        x=src_df['time'], y=src_df['mld_temp'],
        mode='lines',
        line=dict(color=color_T, width=1.5, dash='dot'),
        name=f'{src_label} ΔT=0.2°C',
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>MLD=%{y:.1f} m<extra>'+src_label+' temp</extra>',
    ))

fig5.add_vline(x=CPA_TIME, line=dict(color='black', width=1.5, dash='dash'))
fig5.add_hline(y=REF_DEPTH, line=dict(color='gray', width=1, dash='dot'),
               annotation_text=f'ref depth = {REF_DEPTH:.0f} m', annotation_position='bottom right')

fig5.update_yaxes(
    title='MLD (m, positive down)',
    autorange='reversed',
)
fig5.update_xaxes(title='Time (UTC)')
fig5.update_layout(
    title=dict(
        text='<b>Figure 5</b> — Mixed-layer depth vs. time, obs vs. DOPPIO, two criteria<br>'
             '<sub>Reference depth 25 m (constrained by WFP coverage). Solid: Δσθ=0.03 kg/m³ '
             '(de Boyer Montégut 2004). Dotted: ΔT=0.2°C sensitivity check. Black dashed: CPA.</sub>',
        x=0.5, xanchor='center',
    ),
    height=520, width=1100,
    template='plotly_white',
    legend=dict(x=0.01, y=0.01, yanchor='bottom', bgcolor='rgba(255,255,255,0.85)'),
)
fig5.write_html(FIG_DIR / 'fig05_mld_comparison.html')
fig5
"""
    )
)

# ---- Figure 6: surface T/S ----------------------------------------------
cells.append(
    md(
        """## 7. Figure 6 — Surface T and S time series (T045)

Two panels (T on top, S on bottom), shared time axis. SBI (~0.5 m) vs.
DOPPIO interpolated to 0.5 m. Sub-window shading + CPA line."""
    )
)
cells.append(
    code(
        """fig6 = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    subplot_titles=('Surface temperature (~0.5 m)', 'Surface salinity (~0.5 m)'),
    vertical_spacing=0.10,
)

for r, var, ylabel in [(1, 'T', 'T (°C)'), (2, 'S', 'S (PSU)')]:
    # Sub-window shading
    for x0, x1, c, label in shades:
        fig6.add_vrect(x0=x0, x1=x1, fillcolor=c, line_width=0, row=r, col=1)

    fig6.add_trace(go.Scatter(
        x=sbi_surface['time'], y=sbi_surface[var],
        mode='lines', line=dict(color='#C0392B', width=2),
        name='SBI obs (~0.5 m)', legendgroup='sbi', showlegend=(r == 1),
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>'+var+'=%{y:.3f}<extra>SBI</extra>',
    ), row=r, col=1)
    fig6.add_trace(go.Scatter(
        x=dp_surface['time'], y=dp_surface[var],
        mode='lines', line=dict(color='#2980B9', width=2),
        name='DOPPIO (~0.5 m)', legendgroup='doppio', showlegend=(r == 1),
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>'+var+'=%{y:.3f}<extra>DOPPIO</extra>',
    ), row=r, col=1)
    fig6.add_vline(x=CPA_TIME, line=dict(color='black', width=1.5, dash='dash'),
                   row=r, col=1)
    fig6.update_yaxes(title=ylabel, row=r, col=1)

fig6.update_xaxes(title='Time (UTC)', row=2, col=1)
fig6.update_layout(
    title=dict(
        text='<b>Figure 6</b> — Surface temperature and salinity, obs vs. DOPPIO<br>'
             '<sub>SBI CTD (~0.5 m) vs. DOPPIO interpolated to 0.5 m. '
             'Sub-window shading: pre-storm / storm / recovery. Black dashed: CPA.</sub>',
        x=0.5, xanchor='center',
    ),
    height=650, width=1100,
    template='plotly_white',
    legend=dict(x=0.01, y=0.99, yanchor='top', bgcolor='rgba(255,255,255,0.85)'),
)
fig6.write_html(FIG_DIR / 'fig06_surface_TS.html')
fig6
"""
    )
)

# ---- Table 1: comparison stats ------------------------------------------
cells.append(
    md(
        """## 8. Table 1 — Comparison statistics per sub-window (T043, T046)

For each sub-window, compute bias, RMSE, correlation, and N for:

- Surface T (SBI vs DOPPIO surface)
- Surface S (SBI vs DOPPIO surface)
- MLD density (WFP vs DOPPIO)

Paired on common hourly timestamps within each sub-window."""
    )
)
cells.append(
    code(
        """def paired_stats(obs_df, mod_df, var, t0, t1, label_var, label_window):
    obs = obs_df[['time', var]].rename(columns={var: 'obs'}).copy()
    mod = mod_df[['time', var]].rename(columns={var: 'mod'}).copy()
    obs['time'] = obs['time'].dt.floor('h')
    mod['time'] = mod['time'].dt.floor('h')
    merged = obs.merge(mod, on='time', how='inner')
    merged = merged[(merged['time'] >= t0) & (merged['time'] < t1)].dropna(subset=['obs', 'mod'])
    n = len(merged)
    if n < 2:
        return {'variable': label_var, 'subwindow': label_window, 'N': n,
                'bias': np.nan, 'rmse': np.nan, 'r': np.nan}
    diff = merged['mod'] - merged['obs']
    return {
        'variable':  label_var,
        'subwindow': label_window,
        'N':         n,
        'bias':      float(diff.mean()),
        'rmse':      float(np.sqrt((diff ** 2).mean())),
        'r':         float(np.corrcoef(merged['obs'], merged['mod'])[0, 1]),
    }

# MLD comparison: use mld_sigma (density criterion, primary)
mld_wfp_ren    = mld_wfp.rename(columns={'mld_sigma': 'MLD'})[['time', 'MLD']]
mld_doppio_ren = mld_doppio.rename(columns={'mld_sigma': 'MLD'})[['time', 'MLD']]

stats_rows = []
for (t0, t1, label) in [
    (PRE_START, PRE_END, 'pre-storm'),
    (STORM_START, STORM_END, 'storm'),
    (REC_START, REC_END, 'recovery'),
]:
    stats_rows.append(paired_stats(sbi_surface, dp_surface, 'T', t0, t1, 'surface_T', label))
    stats_rows.append(paired_stats(sbi_surface, dp_surface, 'S', t0, t1, 'surface_S', label))
    stats_rows.append(paired_stats(mld_wfp_ren, mld_doppio_ren, 'MLD', t0, t1, 'MLD_sigma', label))

stats = pd.DataFrame(stats_rows)
stats_round = stats.copy()
for col in ('bias', 'rmse', 'r'):
    stats_round[col] = stats_round[col].round(3)

STATS_OUT = TBL_DIR / 'comparison_stats.csv'
stats_round.to_csv(STATS_OUT, index=False)
print(f'Wrote: {STATS_OUT}')
print()
print(stats_round.to_string(index=False))
"""
    )
)

# ---- Table 2: provenance -------------------------------------------------
cells.append(md("## 9. Table 2 — Data provenance (T047)"))
cells.append(
    code(
        """prov = pd.DataFrame([
    dict(item='obs_WFP_refdes', value='CP13NOPM-WFP01-03-CTDPFK000',
         stream='recovered_wfp', path=str(RAW_DIR / 'CP13NOPM-WFP01-03-CTDPFK000_erin.nc')),
    dict(item='obs_SBI_refdes', value='CP13NOPM-SBI01-02-CTDMOS011',
         stream='recovered_inst', path=str(RAW_DIR / 'CP13NOPM-SBI01-02-CTDMOS011_erin.nc')),
    dict(item='doppio_url', value='https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best',
         stream='operational 2017_da', path=str(RAW_DIR / 'doppio_CP13N_erin.nc')),
    dict(item='nhc_tcr_url', value='https://www.nhc.noaa.gov/data/tcr/AL052025_Erin.pdf',
         stream='best track (Table 1)', path=str(RAW_DIR / 'erin_nhc_besttrack.csv')),
    dict(item='event_window', value='2025-08-15 to 2025-08-29 UTC', stream='', path=''),
    dict(item='cpa', value='2025-08-21 12:00 UTC', stream='', path=''),
    dict(item='MLD_criterion_primary', value=f'Δσθ={DSIG_THRESH} kg/m³',
         stream=f'ref_depth={REF_DEPTH} m', path='de Boyer Montégut 2004'),
    dict(item='MLD_criterion_sensitivity', value=f'ΔT={DT_THRESH} °C',
         stream=f'ref_depth={REF_DEPTH} m', path='Kara et al. 2000 style'),
    dict(item='doppio_interp', value='nearest-neighbour rho-point + per-time interp in depth',
         stream='eta=3, xi=3 of ±3 buffer', path=''),
    dict(item='time_cadence', value='hourly', stream='coarsen, not upsample', path=''),
])
PROV_OUT = TBL_DIR / 'data_provenance.csv'
prov.to_csv(PROV_OUT, index=False)
print(f'Wrote: {PROV_OUT}')
prov
"""
    )
)

# ---- QC -----------------------------------------------------------------
cells.append(md("## 10. QC checks (T048–T050)"))
cells.append(
    code(
        """# T048 — Peak surface cooling should align (±few hours) with CPA
sbi_T = sbi_surface.dropna(subset=['T']).copy()
window = (sbi_T['time'] >= pd.Timestamp('2025-08-18')) & (sbi_T['time'] <= pd.Timestamp('2025-08-25'))
local_min_t = sbi_T.loc[window].sort_values('T').iloc[0]['time']
print(f'Obs SBI peak cooling time: {local_min_t}')
print(f'  offset from CPA (2025-08-21 12 UTC): {(local_min_t - CPA_TIME).total_seconds() / 3600:+.1f} hours')

dp_T = dp_surface.dropna(subset=['T']).copy()
window_d = (dp_T['time'] >= pd.Timestamp('2025-08-18')) & (dp_T['time'] <= pd.Timestamp('2025-08-25'))
local_min_d = dp_T.loc[window_d].sort_values('T').iloc[0]['time']
print(f'DOPPIO peak cooling time:  {local_min_d}')
print(f'  offset from CPA: {(local_min_d - CPA_TIME).total_seconds() / 3600:+.1f} hours')
"""
    )
)
cells.append(
    code(
        """# T049 — N check per sub-window per variable
print('=== Sample sizes per sub-window (Table 1) ===')
n_ok = (stats['N'] >= 12).all()
print(stats[['variable', 'subwindow', 'N']].to_string(index=False))
print(f'\\nAll sub-windows have N >= 12? {n_ok}')
if not n_ok:
    print('WARNING: some sub-windows have N < 12; stats may be unreliable.')
"""
    )
)
cells.append(
    code(
        """# T050 — verify all 6 figures + 2 tables present
fig_names = [f'fig0{i}_*.html' for i in range(1, 7)]
print('Figures:')
for pattern in fig_names:
    matches = sorted(FIG_DIR.glob(pattern))
    for m in matches:
        print(f'  [OK]  {m.name}  ({m.stat().st_size / 1e3:.0f} KB)')
    if not matches:
        print(f'  [MISSING]  {pattern}')
print('\\nTables:')
for name in ('comparison_stats.csv', 'data_provenance.csv'):
    p = TBL_DIR / name
    status = 'OK' if p.exists() else 'MISSING'
    print(f'  [{status}]  {p.name}  ({p.stat().st_size / 1e3:.1f} KB)' if p.exists() else f'  [MISSING]  {name}')
"""
    )
)

# ---- Summary ------------------------------------------------------------
cells.append(
    md(
        """## Summary

Spec 001 deliverables:

| Output | Path |
|---|---|
| Fig 1 — Storm track | `outputs/figures/001-erin-mab-response/fig01_storm_track.html` |
| Fig 2 — Obs T Hovmöller | `outputs/figures/001-erin-mab-response/fig02_obs_temp_hovmoller.html` |
| Fig 3 — DOPPIO T Hovmöller | `outputs/figures/001-erin-mab-response/fig03_doppio_temp_hovmoller.html` |
| Fig 4 — 4-panel T/S | `outputs/figures/001-erin-mab-response/fig04_obs_vs_doppio_TS.html` |
| Fig 5 — MLD comparison | `outputs/figures/001-erin-mab-response/fig05_mld_comparison.html` |
| Fig 6 — Surface T/S | `outputs/figures/001-erin-mab-response/fig06_surface_TS.html` |
| Table 1 — Stats | `outputs/tables/001-erin-mab-response/comparison_stats.csv` |
| Table 2 — Provenance | `outputs/tables/001-erin-mab-response/data_provenance.csv` |

Next: Phase 6 — documentation, pytest, end-to-end reproducibility, PR."""
    )
)

# ---- Build --------------------------------------------------------------
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

out_path = Path(__file__).parent / "04_mixed_layer_response.ipynb"
with out_path.open("w") as f:
    nbf.write(nb, f)

print(f"Wrote {out_path}")
print(f"  cells: {len(cells)} ({sum(1 for c in cells if c.cell_type == 'markdown')} md, {sum(1 for c in cells if c.cell_type == 'code')} code)")
