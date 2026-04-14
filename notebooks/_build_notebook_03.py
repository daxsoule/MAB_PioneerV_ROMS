"""Build notebooks/03_hovmoller_comparison.ipynb from cell definitions.

Run with:  uv run python notebooks/_build_notebook_03.py

Phase 4 of spec 001: Figures 1-4 (storm track + Hovmollers).
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
        """# Spec 001 — Notebook 03: Storm track + Hovmöller comparison (Phase 4)

Produces the first four deliverable figures of spec 001 from the
processed Parquet files written by notebook 02:

- **Figure 1**: Hurricane Erin's NHC best-track path, with MAB South
  array and closest-approach point annotated.
- **Figure 2**: Observation T(z, t) Hovmöller at CP13NOPM across the
  event window.
- **Figure 3**: DOPPIO T(z, t) Hovmöller at the nearest rho-point,
  same window, same color scale.
- **Figure 4**: Side-by-side obs vs DOPPIO for T and S (4 panels).

All figures use Plotly per constitution (student-tier / interactive).
Figures are written to `outputs/figures/001-erin-mab-response/`.""",
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
    'plotly>=5.20'
"""
    )
)

# ---- Constants ------------------------------------------------------------
cells.append(md("## 2. Load inputs and set up paths"))
cells.append(
    code(
        """from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import xarray as xr
from plotly.subplots import make_subplots

PROC_DIR  = Path('../outputs/data/processed')
RAW_DIR   = Path('../outputs/data/raw')
FIG_DIR   = Path('../outputs/figures/001-erin-mab-response')
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Processed Parquet
wfp    = pd.read_parquet(PROC_DIR / 'obs_profile_CP13N_erin.parquet')
sbi    = pd.read_parquet(PROC_DIR / 'obs_surface_CP13N_erin.parquet')
doppio = pd.read_parquet(PROC_DIR / 'doppio_profile_CP13N_erin.parquet')

# Storm track (raw CSV, tracked in git)
track = pd.read_csv(RAW_DIR / 'erin_nhc_besttrack.csv', parse_dates=['datetime_utc'])
# Strip tz so plotting matches the tz-naive obs/DOPPIO convention
track['datetime_utc'] = track['datetime_utc'].dt.tz_convert(None)

# Event anchors (tz-naive UTC)
EVENT_START = pd.Timestamp('2025-08-15')
EVENT_END   = pd.Timestamp('2025-08-29')
CPA_TIME    = pd.Timestamp('2025-08-21 12:00')

# CP13N mooring position — read once from the raw WFP NetCDF attribute.
_wfp_raw = xr.open_dataset(RAW_DIR / 'CP13NOPM-WFP01-03-CTDPFK000_erin.nc')
CP13N_LAT = float(_wfp_raw.lat.values.flat[0])
CP13N_LON = float(_wfp_raw.lon.values.flat[0])
_wfp_raw.close()
print(f'CP13N: {CP13N_LAT:.4f}°N, {CP13N_LON:.4f}°E')

print(f'wfp:    {len(wfp):,} cells ({wfp.time.nunique()} times x {wfp.depth.nunique()} depths)')
print(f'sbi:    {len(sbi):,} hourly bins')
print(f'doppio: {len(doppio):,} cells ({doppio.time.nunique()} times x {doppio.depth.nunique()} depths)')
print(f'track:  {len(track)} positions, {track.datetime_utc.min()} → {track.datetime_utc.max()}')
"""
    )
)

# ---- Figure 1: storm track map ------------------------------------------
cells.append(
    md(
        """## 3. Figure 1 — Hurricane Erin track with MAB South array (T032)

**What this figure shows**: Erin's 6-hourly best-track positions from
NHC (AL052025), colored by storm intensity category. The CP13NOPM
mooring at ~37.1°N, 75.1°W is marked. Erin's closest approach on
2025-08-21 12:00 UTC passed ~378 km SE of the array as a Cat-2
hurricane (90 kt, 949 mb).

**Why it matters**: The mooring was never in the eye, but the storm
was close enough for its wind field to force mixing and surface
cooling across the shelf — that's the signal we'll quantify in the
next figures."""
    )
)
cells.append(
    code(
        """# Plain Cartesian plot — robust across environments (no geo basemap required).
# Axes: longitude (x) x latitude (y), aspect corrected at ~40°N via figure sizing.

CAT_COLORS = {
    'TD': '#7FB3D5', 'TS': '#3498DB',
    'HU1': '#F4D03F', 'HU2': '#F5B041', 'HU3': '#E67E22',
    'HU4': '#E74C3C', 'HU5': '#8B0000',
    'EX': '#7F8C8D',
}

# Coarse US East Coast outline (approximate, for reference only)
COAST_LON = [-81.5, -80.9, -80.0, -78.7, -77.9, -76.3, -76.0, -75.3, -75.0,
             -74.2, -74.0, -73.8, -72.8, -72.0, -71.0, -70.5, -69.8, -69.0,
             -68.0, -66.8, -66.0, -64.5, -61.0, -59.6]
COAST_LAT = [ 30.7,  31.9,  32.8,  33.8,  34.4,  36.2,  37.0,  38.0,  38.8,
              39.5,  40.4,  40.8,  41.2,  41.3,  41.5,  41.8,  42.7,  43.4,
              43.9,  44.7,  45.2,  45.5,  45.3,  45.5]

fig1 = go.Figure()

# Coast outline
fig1.add_trace(
    go.Scatter(
        x=COAST_LON, y=COAST_LAT,
        mode='lines',
        line=dict(color='#888', width=1.5),
        name='US East Coast (approx.)',
        hoverinfo='skip',
        showlegend=False,
    )
)

# Track line
fig1.add_trace(
    go.Scatter(
        x=track['lon'], y=track['lat'],
        mode='lines',
        line=dict(color='#2C3E50', width=2),
        name='Erin track',
        hoverinfo='skip',
    )
)

# Per-fix points colored by intensity category
for cat, color in CAT_COLORS.items():
    sub = track[track.status == cat]
    if sub.empty:
        continue
    fig1.add_trace(
        go.Scatter(
            x=sub['lon'], y=sub['lat'],
            mode='markers',
            marker=dict(size=9, color=color, line=dict(color='white', width=0.5)),
            name=cat,
            hovertemplate='%{customdata[0]}<br>%{customdata[1]} UTC<br>lat=%{y:.2f}°N, lon=%{x:.2f}°E<br>wind=%{customdata[2]} kt, slp=%{customdata[3]} mb<extra></extra>',
            customdata=np.stack([
                [cat] * len(sub),
                sub['datetime_utc'].dt.strftime('%Y-%m-%d %H:%M'),
                sub['wind_kt'].values,
                sub['slp_mb'].values,
            ], axis=-1),
        )
    )

# CPA marker
cpa = track[track.datetime_utc == CPA_TIME].iloc[0]
fig1.add_trace(
    go.Scatter(
        x=[cpa.lon], y=[cpa.lat],
        mode='markers+text',
        marker=dict(size=16, color='black', symbol='x', line=dict(color='black', width=2)),
        text=['CPA 2025-08-21 12 UTC'],
        textposition='middle right',
        textfont=dict(size=10),
        name='Closest approach',
        hoverinfo='skip',
    )
)

# CP13NOPM mooring star
fig1.add_trace(
    go.Scatter(
        x=[CP13N_LON], y=[CP13N_LAT],
        mode='markers+text',
        marker=dict(size=18, color='#27AE60', symbol='star', line=dict(color='white', width=1)),
        text=['  CP13NOPM'],
        textposition='middle right',
        textfont=dict(size=12, color='#27AE60'),
        name='CP13NOPM (MAB South)',
        hoverinfo='skip',
    )
)

fig1.update_xaxes(
    title='Longitude (°E)',
    range=[-85, -5],
    zeroline=False, showgrid=True, gridcolor='#EEE',
)
fig1.update_yaxes(
    title='Latitude (°N)',
    range=[10, 65],
    zeroline=False, showgrid=True, gridcolor='#EEE',
    scaleanchor='x', scaleratio=1.3,  # approximate aspect at 40°N (1/cos(40°)≈1.31)
)
fig1.update_layout(
    title=dict(
        text='<b>Figure 1</b> — Hurricane Erin (AL052025) NHC best track<br>'
             '<sub>Closest approach ~380 km SE of CP13NOPM on 2025-08-21 12:00 UTC (Cat 2)</sub>',
        x=0.5, xanchor='center',
    ),
    height=700, width=1000,
    template='plotly_white',
    legend=dict(x=0.02, y=0.02, yanchor='bottom', bgcolor='rgba(255,255,255,0.85)'),
    plot_bgcolor='#F3F8FC',
)

fig1.write_html(FIG_DIR / 'fig01_storm_track.html')
fig1
"""
    )
)

# ---- Figure 2: obs T Hovmöller -------------------------------------------
cells.append(
    md(
        """## 4. Figure 2 — Observation T(z, t) Hovmöller (T033)

WFP profiler T at CP13NOPM on the 2 m × hourly grid. The closest-
approach time is marked (dashed black line).

**What to look for**: bottom-layer temperature should be roughly
stable around 12–14 °C during the quiescent pre-storm days, with
upper warm water sitting above 50 m. During Erin's passage, wind-
driven mixing should cool the upper layer and deepen the thermocline
— look for a visible tongue of cool water reaching upward."""
    )
)
cells.append(
    code(
        """wfp_pv = wfp.pivot(index='depth', columns='time', values='T').sort_index()

TEMP_MIN, TEMP_MAX = 10.0, 26.0   # °C, common scale for Figures 2-4

# Two-row layout: top strip = SBI surface T time series;
# main panel = WFP Hovmoller (25-79 m). 0.5-25 m is unsampled (documented gap).
fig2 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    row_heights=[0.22, 0.78],
    vertical_spacing=0.05,
    subplot_titles=('SBI near-surface T (~0.5 m)', 'WFP profile T (25–79 m)'),
)

# Top strip: SBI surface time series
fig2.add_trace(
    go.Scatter(
        x=sbi['time'], y=sbi['T'],
        mode='lines',
        line=dict(color='#C0392B', width=2),
        name='SBI ~0.5 m',
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>T=%{y:.2f} °C<extra>SBI surface</extra>',
    ),
    row=1, col=1,
)

# Main panel: WFP Hovmoller
fig2.add_trace(
    go.Heatmap(
        x=wfp_pv.columns, y=wfp_pv.index, z=wfp_pv.values,
        zmin=TEMP_MIN, zmax=TEMP_MAX,
        colorscale='RdYlBu_r',
        colorbar=dict(title='T (°C)', y=0.39, len=0.78),
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>depth=%{y:.1f} m<br>T=%{z:.2f} °C<extra>WFP</extra>',
    ),
    row=2, col=1,
)

# CPA line on both panels
fig2.add_vline(x=CPA_TIME, line=dict(color='black', width=1.2, dash='dash'), row=1, col=1)
fig2.add_vline(x=CPA_TIME, line=dict(color='black', width=1.2, dash='dash'), row=2, col=1)

fig2.update_yaxes(title='T (°C)', row=1, col=1, range=[TEMP_MIN, TEMP_MAX])
fig2.update_yaxes(title='Depth (m)', autorange='reversed', row=2, col=1)
fig2.update_xaxes(title='Time (UTC)', row=2, col=1)

fig2.update_layout(
    title=dict(
        text='<b>Figure 2</b> — Observed temperature at CP13NOPM during Hurricane Erin<br>'
             '<sub>Top: SBI surface CTD time series. Bottom: WFP profiler Hovmöller. '
             'Depth gap 0.5–25 m is unsampled on this mooring.</sub>',
        x=0.5, xanchor='center',
    ),
    height=680, width=1100,
    template='plotly_white',
    showlegend=False,
)
fig2.write_html(FIG_DIR / 'fig02_obs_temp_hovmoller.html')
fig2
"""
    )
)

# ---- Figure 3: DOPPIO T Hovmöller ----------------------------------------
cells.append(
    md(
        """## 5. Figure 3 — DOPPIO T(z, t) Hovmöller (T034)

DOPPIO operational (`2017_da`, `History_Best`) T at the nearest
rho-point to CP13NOPM, on the same 2 m × hourly grid as Figure 2.
Same color scale for direct comparison.

**What to look for**: Is the mean thermal structure similar? Does
DOPPIO produce a comparable mixing response in timing and amplitude?
Any discrete features — e.g., step-changes at specific hours — may
reflect data-assimilation increments, not physical forcing."""
    )
)
cells.append(
    code(
        """doppio_pv = doppio.pivot(index='depth', columns='time', values='T').sort_index()

# DOPPIO surface T — we need the topmost sigma level's T at the center
# rho-point, interpolated at ~0.5 m depth for apples-to-apples with SBI.
# The processed doppio parquet was gridded 25-79 m, but the raw DOPPIO
# slice has the full column. Load it and pull surface T.
import xarray as xr
_dp_raw = xr.open_dataset(RAW_DIR / 'doppio_CP13N_erin.nc')
# z reconstruct at center rho-point (eta=3, xi=3)
h_c    = float(_dp_raw.h.isel(eta_rho=3, xi_rho=3).values)
Cs_r   = _dp_raw.Cs_r.values
hc_v   = float(_dp_raw.hc.values)
s_rho  = _dp_raw.s_rho.values
zeta_c = _dp_raw.zeta.isel(eta_rho=3, xi_rho=3).values
temp_c = _dp_raw.temp.isel(eta_rho=3, xi_rho=3).values  # (time, s_rho)
# Vtransform=2
S = (hc_v * s_rho + h_c * Cs_r) / (hc_v + h_c)
z = zeta_c[:, None] + (zeta_c[:, None] + h_c) * S[None, :]  # positive up
z_down = -z
# For each time, interpolate T at depth ~0.5 m (match SBI).
doppio_surface_T = np.array([
    np.interp(0.5, np.sort(z_down[t_i]), temp_c[t_i][np.argsort(z_down[t_i])])
    for t_i in range(z_down.shape[0])
])
doppio_surface_time = pd.to_datetime(_dp_raw.time.values)
_dp_raw.close()

fig3 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    row_heights=[0.22, 0.78],
    vertical_spacing=0.05,
    subplot_titles=('DOPPIO surface T (~0.5 m, interpolated)', 'DOPPIO profile T (25–79 m)'),
)

# Top strip: DOPPIO surface time series
fig3.add_trace(
    go.Scatter(
        x=doppio_surface_time, y=doppio_surface_T,
        mode='lines',
        line=dict(color='#2980B9', width=2),
        name='DOPPIO ~0.5 m',
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>T=%{y:.2f} °C<extra>DOPPIO surface</extra>',
    ),
    row=1, col=1,
)

# Main panel: DOPPIO Hovmoller (same 25-79 m grid as obs for apples-to-apples)
fig3.add_trace(
    go.Heatmap(
        x=doppio_pv.columns, y=doppio_pv.index, z=doppio_pv.values,
        zmin=TEMP_MIN, zmax=TEMP_MAX,
        colorscale='RdYlBu_r',
        colorbar=dict(title='T (°C)', y=0.39, len=0.78),
        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>depth=%{y:.1f} m<br>T=%{z:.2f} °C<extra>DOPPIO</extra>',
    ),
    row=2, col=1,
)

fig3.add_vline(x=CPA_TIME, line=dict(color='black', width=1.2, dash='dash'), row=1, col=1)
fig3.add_vline(x=CPA_TIME, line=dict(color='black', width=1.2, dash='dash'), row=2, col=1)

fig3.update_yaxes(title='T (°C)', row=1, col=1, range=[TEMP_MIN, TEMP_MAX])
fig3.update_yaxes(title='Depth (m)', autorange='reversed', row=2, col=1)
fig3.update_xaxes(title='Time (UTC)', row=2, col=1)

fig3.update_layout(
    title=dict(
        text='<b>Figure 3</b> — DOPPIO temperature at nearest rho-point to CP13NOPM<br>'
             '<sub>Top: DOPPIO surface time series (interpolated to ~0.5 m for compare). '
             'Bottom: DOPPIO Hovmöller 25–79 m (matches obs Hovmöller in Figure 2).</sub>',
        x=0.5, xanchor='center',
    ),
    height=680, width=1100,
    template='plotly_white',
    showlegend=False,
)
fig3.write_html(FIG_DIR / 'fig03_doppio_temp_hovmoller.html')
fig3
"""
    )
)

# ---- Figure 4: 2x2 side-by-side -----------------------------------------
cells.append(
    md(
        """## 6. Figure 4 — Side-by-side obs vs. DOPPIO for T and S (T035)

Four panels, common color scale per variable:

- **(a)** obs T — **(b)** DOPPIO T
- **(c)** obs S — **(d)** DOPPIO S

Same depth and time axes as Figures 2–3. CPA marked on every panel."""
    )
)
cells.append(
    code(
        """wfp_T    = wfp.pivot(index='depth', columns='time', values='T').sort_index()
doppio_T = doppio.pivot(index='depth', columns='time', values='T').sort_index()
wfp_S    = wfp.pivot(index='depth', columns='time', values='S').sort_index()
doppio_S = doppio.pivot(index='depth', columns='time', values='S').sort_index()

# Shared ranges per variable
tmin = min(np.nanmin(wfp_T.values), np.nanmin(doppio_T.values))
tmax = max(np.nanmax(wfp_T.values), np.nanmax(doppio_T.values))
smin = min(np.nanmin(wfp_S.values), np.nanmin(doppio_S.values))
smax = max(np.nanmax(wfp_S.values), np.nanmax(doppio_S.values))

fig4 = make_subplots(
    rows=2, cols=2,
    subplot_titles=('(a) obs T', '(b) DOPPIO T', '(c) obs S', '(d) DOPPIO S'),
    shared_xaxes=True, shared_yaxes=True,
    horizontal_spacing=0.10, vertical_spacing=0.12,
)

# Row 1: temperature
fig4.add_trace(
    go.Heatmap(x=wfp_T.columns, y=wfp_T.index, z=wfp_T.values,
               zmin=tmin, zmax=tmax, colorscale='RdYlBu_r',
               colorbar=dict(title='T (°C)', x=0.46, y=0.77, len=0.35, yanchor='middle')),
    row=1, col=1,
)
fig4.add_trace(
    go.Heatmap(x=doppio_T.columns, y=doppio_T.index, z=doppio_T.values,
               zmin=tmin, zmax=tmax, colorscale='RdYlBu_r', showscale=False),
    row=1, col=2,
)
# Row 2: salinity
fig4.add_trace(
    go.Heatmap(x=wfp_S.columns, y=wfp_S.index, z=wfp_S.values,
               zmin=smin, zmax=smax, colorscale='Viridis',
               colorbar=dict(title='S (PSU)', x=0.46, y=0.23, len=0.35, yanchor='middle')),
    row=2, col=1,
)
fig4.add_trace(
    go.Heatmap(x=doppio_S.columns, y=doppio_S.index, z=doppio_S.values,
               zmin=smin, zmax=smax, colorscale='Viridis', showscale=False),
    row=2, col=2,
)

# CPA line on all four panels
for r in (1, 2):
    for c in (1, 2):
        fig4.add_vline(x=CPA_TIME, line=dict(color='black', width=1, dash='dash'), row=r, col=c)

# Axes: depth reversed everywhere, titles on bottom-left
for r in (1, 2):
    for c in (1, 2):
        fig4.update_yaxes(autorange='reversed', row=r, col=c)
fig4.update_yaxes(title='Depth (m)', row=1, col=1)
fig4.update_yaxes(title='Depth (m)', row=2, col=1)
fig4.update_xaxes(title='Time (UTC)', row=2, col=1)
fig4.update_xaxes(title='Time (UTC)', row=2, col=2)

fig4.update_layout(
    title=dict(
        text='<b>Figure 4</b> — Side-by-side obs vs. DOPPIO T and S at CP13NOPM during Erin<br>'
             '<sub>Rows: T (top), S (bottom). Columns: obs WFP (left), DOPPIO (right). Black dashed: CPA.</sub>',
        x=0.5, xanchor='center',
    ),
    height=800, width=1200,
    template='plotly_white',
)
fig4.write_html(FIG_DIR / 'fig04_obs_vs_doppio_TS.html')
fig4
"""
    )
)

# ---- QC + summary -------------------------------------------------------
cells.append(md("## 7. QC — verify all four figure files present (T037)"))
cells.append(
    code(
        """expected = [
    'fig01_storm_track.html',
    'fig02_obs_temp_hovmoller.html',
    'fig03_doppio_temp_hovmoller.html',
    'fig04_obs_vs_doppio_TS.html',
]
print(f'Figures in {FIG_DIR}:')
for name in expected:
    p = FIG_DIR / name
    status = 'OK' if p.exists() else 'MISSING'
    size = f'{p.stat().st_size / 1e3:.1f} KB' if p.exists() else '-'
    print(f'  [{status}] {name:40s}  {size}')
"""
    )
)

cells.append(
    md(
        """## Summary

Four interactive Plotly figures written to
`outputs/figures/001-erin-mab-response/`:

- `fig01_storm_track.html`
- `fig02_obs_temp_hovmoller.html`
- `fig03_doppio_temp_hovmoller.html`
- `fig04_obs_vs_doppio_TS.html`

Next: notebook 04 — MLD + surface time series + comparison statistics."""
    )
)

# ---- Build ----------------------------------------------------------
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}

out_path = Path(__file__).parent / "03_hovmoller_comparison.ipynb"
with out_path.open("w") as f:
    nbf.write(nb, f)

print(f"Wrote {out_path}")
print(f"  cells: {len(cells)} ({sum(1 for c in cells if c.cell_type == 'markdown')} md, {sum(1 for c in cells if c.cell_type == 'code')} code)")
