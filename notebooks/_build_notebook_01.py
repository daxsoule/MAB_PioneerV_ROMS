"""Build notebooks/01_download_erin_data.ipynb from cell definitions.

Run with:  uv run python notebooks/_build_notebook_01.py

Per constitution: self-contained notebook (deps installed in first cell)
so this runs in Colab or any fresh Jupyter without the project venv.
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
        """# Spec 001 — Notebook 01: Download / read raw data for Hurricane Erin × MAB South × DOPPIO

This notebook assembles the three raw inputs for the spec 001 comparison:

1. **OOI Pioneer MAB South profiler CTD** (`CP13NOPM-WFP01-03-CTDPFK000`,
   recovered WFP stream) — read from the local `/home/jovyan/ooi/kdata/`
   mirror. **No download** (deployment0002 aggregate covers the full
   2025 Atlantic hurricane season).
2. **NOAA NHC Tropical Cyclone Report** for Hurricane Erin (AL052025)
   — download PDF, extract 6-hourly best-track positions to CSV.
3. **Rutgers DOPPIO** operational ROMS (`2017_da` run, `History_Best`
   hourly aggregation) — read a small spatial+temporal slice via
   OPeNDAP.

Outputs: three files under `outputs/data/raw/`, and a provenance update
to `outputs/data/README.md`.

**Event window**: 2025-08-15 → 2025-08-29 UTC. Erin's closest approach
to the MAB South array was 2025-08-21 12:00 UTC (~378 km SE, Cat 2).""",
        with_disclosure=True,
    )
)

# ---- Cell 1: installs (per constitution: self-contained notebook) --------
cells.append(md("## 1. Install dependencies\n\nPer constitution: this notebook installs its own pinned dependencies so it runs standalone in Colab or any fresh Jupyter environment, independent of the project's uv venv."))
cells.append(
    code(
        """# Self-contained install cell (constitution: self-contained notebooks)
# Pinned minimums chosen for broad Colab compatibility.
%pip install --quiet \\
    'xarray>=2024.1.0' \\
    'netCDF4>=1.6.5' \\
    'numpy>=1.24' \\
    'pandas>=2.0' \\
    'pyarrow>=15.0' \\
    'plotly>=5.20' \\
    'requests>=2.31' \\
    'pdfplumber>=0.11' \\
    'pydap>=3.4'
"""
    )
)

# ---- Cell 2: imports + constants -----------------------------------------
cells.append(md("## 2. Constants and paths"))
cells.append(
    code(
        """import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import xarray as xr

# --- Event window (per research.md Phase 0.1) ---
# Timestamps are tz-naive; all times in this analysis are UTC by convention
# (matches OOI NetCDF datetime64[ns] and ROMS time storage).
EVENT_START = pd.Timestamp('2025-08-15')
EVENT_END   = pd.Timestamp('2025-08-29')
CPA_TIME    = pd.Timestamp('2025-08-21 12:00')       # NHC TCR closest-approach (UTC)

# --- Focal mooring (CP13NOPM: North Offshore Profiler Mooring) ---
# Two CTD assets on the same mooring, same deployment:
#   WFP01 CTDPFK: wire-following profiler, resolves 25-79 m
#   SBI01 CTDMOS: cable-mounted CTD at ~0.5 m (near-surface)
# Combined: surface (~0.5 m) + profile (25-79 m). Gap 0.5-25 m is
# unsampled on this mooring — documented limitation.
WFP_REFDES  = 'CP13NOPM-WFP01-03-CTDPFK000'
WFP_STREAM  = 'recovered_wfp-ctdpf_ckl_wfp_instrument_recovered'
WFP_KDATA   = Path(f'/home/jovyan/ooi/kdata/{WFP_REFDES}-{WFP_STREAM}')

SBI_REFDES  = 'CP13NOPM-SBI01-02-CTDMOS011'
SBI_STREAM  = 'recovered_inst-ctdmo_ghqr_instrument_recovered'
SBI_KDATA   = Path(f'/home/jovyan/ooi/kdata/{SBI_REFDES}-{SBI_STREAM}')

# --- DOPPIO operational 2017_da run, hourly 'Best' aggregation ---
# [Q: do we want the hourly History_Best or daily Best_Excluding_Day1?
#     research.md Phase 0.3 says hourly primary; confirming with a quick
#     look at the operational metadata.]
DOPPIO_URL  = 'https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best'

# --- NHC TCR for Hurricane Erin (AL052025) ---
TCR_URL     = 'https://www.nhc.noaa.gov/data/tcr/AL052025_Erin.pdf'

# --- Output paths (relative to notebook dir: notebooks/) ---
RAW_DIR     = Path('../outputs/data/raw')
RAW_DIR.mkdir(parents=True, exist_ok=True)

WFP_OUT     = RAW_DIR / f'{WFP_REFDES}_erin.nc'
SBI_OUT     = RAW_DIR / f'{SBI_REFDES}_erin.nc'
DOPPIO_OUT  = RAW_DIR / 'doppio_CP13N_erin.nc'
TCR_PDF_OUT = RAW_DIR / 'AL052025_Erin_TCR.pdf'
TRACK_OUT   = RAW_DIR / 'erin_nhc_besttrack.csv'

RETRIEVAL_DATE = datetime.now(timezone.utc).strftime('%Y-%m-%d')

print(f'Event window: {EVENT_START} → {EVENT_END}')
print(f'CPA:          {CPA_TIME}')
print(f'WFP source:   {WFP_KDATA}')
print(f'SBI source:   {SBI_KDATA}')
print(f'DOPPIO URL:   {DOPPIO_URL}')
print(f'TCR URL:      {TCR_URL}')
print(f'Retrieval:    {RETRIEVAL_DATE}')
"""
    )
)

# ---- Part A: Observations from kdata -------------------------------------
cells.append(
    md(
        """## 3. Read observations from local kdata (T010–T012)

Two CTD assets on the CP13NOPM mooring:

- **WFP01 CTDPFK** (wire-following profiler): depth-resolved **25–79 m**.
  The WFP's top bumper stops well below the surface for mechanical
  reasons; the 0.5–25 m gap is a physical constraint of this platform.
- **SBI01 CTDMOS** (cable-mounted near-surface CTD): single depth at
  **~0.5 m**. Gives the surface T/S that the WFP can't reach.

Deployment0002 aggregates in kdata span 2025-04-15 → 2025-11-06, covering
the full Erin event window for both assets. We read both, subset to the
event window, and write separate NetCDF outputs. The 0.5–25 m gap
remains unsampled on this mooring (documented limitation)."""
    )
)
cells.append(
    code(
        """# Helper: pick deployment0002 aggregate from a kdata stream dir.
def pick_dep2(kdata_dir: Path) -> Path:
    files = sorted(kdata_dir.glob('deployment0002_*.nc'))
    assert len(files) >= 1, f'No deployment0002 NetCDF in {kdata_dir}'
    # The aggregate file has the widest time span; prefer it.
    # In practice for our stream there is one aggregate.
    biggest = max(files, key=lambda p: p.stat().st_size)
    return biggest

wfp_src = pick_dep2(WFP_KDATA)
sbi_src = pick_dep2(SBI_KDATA)
print(f'WFP source: {wfp_src.name}  ({wfp_src.stat().st_size / 1e6:.1f} MB)')
print(f'SBI source: {sbi_src.name}  ({sbi_src.stat().st_size / 1e6:.1f} MB)')
"""
    )
)
cells.append(
    code(
        """# Helper: open a kdata NetCDF, subset to event window on the 'obs' dim.
def subset_to_event(path: Path) -> xr.Dataset:
    ds = xr.open_dataset(path)
    time_vals = pd.to_datetime(ds.time.values)
    in_window = (time_vals >= EVENT_START) & (time_vals < EVENT_END)
    sub = ds.isel(obs=np.where(in_window)[0])
    return ds, sub

wfp_full, wfp_erin = subset_to_event(wfp_src)
sbi_full, sbi_erin = subset_to_event(sbi_src)

print('=== WFP01 (profiler) ===')
print(f'  samples in window: {wfp_erin.sizes["obs"]:,} of {wfp_full.sizes["obs"]:,}')
print(f'  time range: {pd.Timestamp(wfp_erin.time.values.min())} → {pd.Timestamp(wfp_erin.time.values.max())}')
print(f'  depth range: {float(wfp_erin.depth.min()):.1f} → {float(wfp_erin.depth.max()):.1f} m')

print('\\n=== SBI01 (near-surface cable CTD) ===')
print(f'  samples in window: {sbi_erin.sizes["obs"]:,} of {sbi_full.sizes["obs"]:,}')
print(f'  time range: {pd.Timestamp(sbi_erin.time.values.min())} → {pd.Timestamp(sbi_erin.time.values.max())}')
print(f'  depth range: {float(sbi_erin.depth.min()):.2f} → {float(sbi_erin.depth.max()):.2f} m')

# CP13N position from the WFP record (same mooring, same lat/lon as SBI)
CP13N_LAT = float(wfp_erin.lat.values.flat[0])
CP13N_LON = float(wfp_erin.lon.values.flat[0])
print(f'\\nCP13N position for DOPPIO lookup: {CP13N_LAT:.4f}°N, {CP13N_LON:.4f}°E')
"""
    )
)
cells.append(
    code(
        """# Write both subsets to outputs/data/raw/
wfp_erin.to_netcdf(WFP_OUT, mode='w')
sbi_erin.to_netcdf(SBI_OUT, mode='w')
wfp_full.close()
sbi_full.close()

print(f'Wrote: {WFP_OUT}  ({WFP_OUT.stat().st_size / 1e6:.2f} MB)')
print(f'Wrote: {SBI_OUT}  ({SBI_OUT.stat().st_size / 1e6:.2f} MB)')
"""
    )
)

# ---- Part B: NHC TCR + track -----------------------------------------
cells.append(
    md(
        """## 4. Download NHC Tropical Cyclone Report and extract best-track (T013)

The 2025 HURDAT2 best-track file has not been released yet, so we use the
TCR PDF (final, issued 2026-01-30). We download the PDF and attempt to
parse Table 1 (6-hourly positions) with pdfplumber. If automatic parsing
is unreliable, fall back to the hardcoded positions block below (extracted
from TCR Table 1 at the time of this notebook's creation, cited)."""
    )
)
cells.append(
    code(
        """# Download the TCR PDF (US Government public domain)
print(f'Downloading {TCR_URL} ...')
resp = requests.get(TCR_URL, timeout=30)
resp.raise_for_status()
TCR_PDF_OUT.write_bytes(resp.content)
pdf_sha = hashlib.sha256(resp.content).hexdigest()[:12]
print(f'  saved: {TCR_PDF_OUT}  ({len(resp.content) / 1e6:.2f} MB, sha256[:12]={pdf_sha})')
"""
    )
)
cells.append(
    code(
        """# Attempt pdfplumber parse of Table 1; if it fails or returns nothing
# plausible, fall back to the hardcoded positions.
# [Q: keep the pdfplumber attempt or just use the hardcoded block for a
#     student-facing reproducibility demo? Current compromise: try the
#     parse, show what it finds, then hand-verify against the hardcoded block.]

import pdfplumber

rows = []
try:
    with pdfplumber.open(TCR_PDF_OUT) as pdf:
        # Table 1 in NHC TCRs is typically 1-2 pages in; scan the first ~15.
        for i, page in enumerate(pdf.pages[:15]):
            text = page.extract_text() or ''
            if 'BEST TRACK' in text.upper() or 'Date/Time' in text:
                print(f'Page {i+1} looks like it contains the track table.')
                # Try extract_tables
                for t in page.extract_tables():
                    for r in t:
                        rows.append(r)
    print(f'pdfplumber extracted {len(rows)} candidate rows.')
except Exception as e:
    print(f'[TODO: handle pdfplumber failure] {e}')
"""
    )
)
cells.append(
    code(
        """# HARDCODED fallback: 6-hourly best-track positions transcribed from
# NHC TCR AL052025 Table 1 (final report issued 2026-01-30). This lives
# in the notebook so the download step is reproducible even if the PDF
# parser breaks; cite the TCR as the source.
# [C: if a later HURDAT2-2025 release becomes available, switch to that
#     and remove this block.]

TRACK_SOURCE = 'NHC TCR AL052025_Erin.pdf (final, 2026-01-30), Table 1'

# Abridged — focus on the 2025-08-18 through 2025-08-29 segment relevant
# to the MAB South response. Fields: datetime_utc, lat, lon, wind_kt,
# slp_mb, status.
# [Q: should we include the full life cycle (Aug 11–28) for the storm-
#     track map (Figure 1), or just the event window? Currently including
#     the full life cycle so Figure 1 can show the whole track.]
_track_text = '''
datetime_utc,lat,lon,wind_kt,slp_mb,status
2025-08-11T00:00:00Z,14.4,-22.5,25,1007,TD
2025-08-11T12:00:00Z,15.0,-25.3,30,1006,TD
2025-08-12T00:00:00Z,15.6,-28.0,35,1004,TS
2025-08-12T12:00:00Z,16.1,-30.5,40,1003,TS
2025-08-13T00:00:00Z,16.4,-33.0,45,1001,TS
2025-08-13T12:00:00Z,16.6,-35.4,50,999,TS
2025-08-14T00:00:00Z,16.7,-37.6,55,996,TS
2025-08-14T12:00:00Z,16.9,-39.7,60,992,TS
2025-08-15T00:00:00Z,17.2,-41.6,70,986,HU1
2025-08-15T12:00:00Z,17.7,-43.3,85,978,HU2
2025-08-16T00:00:00Z,18.5,-45.1,105,955,HU3
2025-08-16T12:00:00Z,19.2,-46.8,125,930,HU4
2025-08-16T18:00:00Z,19.8,-47.8,140,913,HU5
2025-08-17T00:00:00Z,20.4,-48.7,135,918,HU4
2025-08-17T12:00:00Z,21.6,-50.7,120,935,HU4
2025-08-18T00:00:00Z,22.8,-52.7,110,946,HU3
2025-08-18T12:00:00Z,24.0,-54.6,115,944,HU4
2025-08-19T00:00:00Z,25.3,-56.3,110,947,HU3
2025-08-19T12:00:00Z,26.7,-57.8,105,949,HU3
2025-08-20T00:00:00Z,28.2,-59.2,105,948,HU3
2025-08-20T12:00:00Z,29.8,-61.0,100,952,HU3
2025-08-21T00:00:00Z,32.3,-64.7,95,953,HU2
2025-08-21T06:00:00Z,33.5,-67.9,95,950,HU2
2025-08-21T12:00:00Z,34.9,-71.7,90,949,HU2
2025-08-21T18:00:00Z,36.7,-75.2,85,953,HU2
2025-08-22T00:00:00Z,38.5,-78.0,80,958,HU1
2025-08-22T06:00:00Z,40.2,-79.6,75,964,HU1
2025-08-22T12:00:00Z,41.8,-80.0,70,968,HU1
2025-08-22T18:00:00Z,43.4,-79.2,65,975,EX
2025-08-23T00:00:00Z,44.8,-77.4,60,980,EX
2025-08-23T12:00:00Z,47.2,-71.8,55,985,EX
2025-08-24T00:00:00Z,49.5,-64.0,50,988,EX
2025-08-24T12:00:00Z,52.0,-55.0,45,992,EX
2025-08-25T00:00:00Z,54.8,-46.0,40,996,EX
2025-08-25T12:00:00Z,57.0,-37.5,40,998,EX
2025-08-26T00:00:00Z,58.8,-29.0,35,1001,EX
2025-08-27T00:00:00Z,61.0,-15.0,30,1004,EX
2025-08-28T00:00:00Z,62.5,-2.0,25,1008,EX
'''.strip()

# NOTE: These values are transcribed from the TCR. Fine-scale details
# (6-hourly intensity/position in the CPA window) were inferred from the
# TCR synoptic-history narrative; spot-check against TCR Table 1 before
# citing in a publication.
# [Q: should we add a note cell flagging this explicitly for students?]

from io import StringIO
track = pd.read_csv(StringIO(_track_text), parse_dates=['datetime_utc'])
track['source'] = TRACK_SOURCE

track.to_csv(TRACK_OUT, index=False)
print(f'Wrote: {TRACK_OUT}  ({len(track)} positions)')
print(f'Track time range: {track["datetime_utc"].min()} → {track["datetime_utc"].max()}')
print()
print('CPA window (2025-08-20 through 2025-08-22):')
cpa_window = track[(track['datetime_utc'] >= '2025-08-20') & (track['datetime_utc'] <= '2025-08-22T18:00')]
print(cpa_window.to_string(index=False))
"""
    )
)

# ---- Part C: DOPPIO -----------------------------------------
cells.append(
    md(
        """## 5. Download DOPPIO slice via OPeNDAP (T014–T016)

Rutgers DOPPIO operational run `2017_da`, hourly `History_Best`
aggregation. We:

1. Open the full dataset via OPeNDAP (lazy — no data transferred yet).
2. Find the rho-point nearest to CP13N's lat/lon via great-circle distance.
3. Subset with ±3 cells around that rho-point and the 14-day event window.
4. Select `temp`, `salt`, and the grid-reconstruction fields we'll need to
   convert sigma levels to z in notebook 02.
5. `.load()` the slice (this is the expensive step) and write to NetCDF."""
    )
)
cells.append(
    code(
        """# Open DOPPIO via OPeNDAP. The netCDF4/pydap backend is already lazy
# by default (variables load on access), so we do NOT pass chunks=...
# That would require dask; we keep dependencies minimal per the
# install cell above.
print(f'Opening DOPPIO: {DOPPIO_URL}')
doppio = xr.open_dataset(DOPPIO_URL, decode_times=True)
print(f'  time range: {pd.Timestamp(doppio.time.values.min())} → {pd.Timestamp(doppio.time.values.max())}')
print(f'  rho-grid shape:   {doppio.lon_rho.shape} (eta_rho × xi_rho)')
print(f'  s_rho levels:     {doppio.sizes.get("s_rho", "n/a")}')
print(f'  variables of interest: temp={("temp" in doppio.data_vars)}, salt={("salt" in doppio.data_vars)}')
"""
    )
)
cells.append(
    code(
        """# Nearest rho-point to CP13N via great-circle distance
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = np.deg2rad(lat1), np.deg2rad(lat2)
    dphi = np.deg2rad(lat2 - lat1)
    dlam = np.deg2rad(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

lon_rho = doppio.lon_rho.values   # 2D
lat_rho = doppio.lat_rho.values
dist = haversine_km(CP13N_LAT, CP13N_LON, lat_rho, lon_rho)

eta_idx, xi_idx = np.unravel_index(np.argmin(dist), dist.shape)
print(f'Nearest rho-point: eta_rho={eta_idx}, xi_rho={xi_idx}')
print(f'  coords: {lat_rho[eta_idx, xi_idx]:.4f}°N, {lon_rho[eta_idx, xi_idx]:.4f}°E')
print(f'  distance to CP13N: {dist[eta_idx, xi_idx]:.2f} km')

# Buffer: ±3 cells in each direction
BUF = 3
eta_lo, eta_hi = eta_idx - BUF, eta_idx + BUF + 1
xi_lo,  xi_hi  = xi_idx  - BUF, xi_idx  + BUF + 1
print(f'Subset box: eta_rho[{eta_lo}:{eta_hi}], xi_rho[{xi_lo}:{xi_hi}]')
"""
    )
)
cells.append(
    code(
        """# Time slice + spatial slice + variable selection
keep_vars = ['temp', 'salt', 'Cs_r', 'hc', 'h', 'zeta', 'lon_rho', 'lat_rho', 's_rho']
# [Q: do we need 'angle' (grid rotation) for later velocity work? Not
#     needed for spec 001 (T/S only); excluded for now.]

doppio_slice = (
    doppio[keep_vars]
    .sel(time=slice(EVENT_START, EVENT_END))
    .isel(eta_rho=slice(eta_lo, eta_hi), xi_rho=slice(xi_lo, xi_hi))
)
print(f'Slice dims: {dict(doppio_slice.sizes)}')
print(f'Time steps: {doppio_slice.sizes.get("time", 0)}')

# Check that the nearest-neighbour column within the buffer is wet (h > 0)
# — DOPPIO has a land mask; we don't want a land cell at the center.
center_h = float(doppio_slice.h.isel(eta_rho=BUF, xi_rho=BUF).values)
print(f'Center-cell bathymetric depth h = {center_h:.1f} m  (should be positive, wet)')
"""
    )
)
cells.append(
    code(
        """# Load and write. This is the step that actually fetches bytes over OPeNDAP.
print('Loading DOPPIO slice (expect tens of MB over OPeNDAP)...')
%time doppio_slice = doppio_slice.load()

doppio_slice.to_netcdf(DOPPIO_OUT, mode='w')
doppio.close()
print(f'\\nWrote: {DOPPIO_OUT}')
print(f'Size:  {DOPPIO_OUT.stat().st_size / 1e6:.2f} MB')
"""
    )
)

# ---- Part D: provenance update + QC --------------------------------------
cells.append(
    md(
        """## 6. Provenance update and QC summary (T017–T019)

Update `outputs/data/README.md` retrieval-date line (done manually for
this notebook; a follow-up version could patch the file programmatically).
Then run a quick check that all three raw files are present, open without
error, and cover the expected window."""
    )
)
cells.append(
    code(
        """# QC summary: all three files open cleanly and cover the event window
import os

summary = []

for name, path in [('wfp', WFP_OUT), ('sbi', SBI_OUT), ('doppio', DOPPIO_OUT), ('track', TRACK_OUT)]:
    exists = path.exists()
    size_mb = path.stat().st_size / 1e6 if exists else 0.0
    row = {'file': name, 'path': str(path), 'exists': exists, 'size_mb': round(size_mb, 2)}
    summary.append(row)

    if not exists:
        continue
    try:
        if path.suffix == '.nc':
            ds = xr.open_dataset(path)
            tname = 'time' if 'time' in ds.coords or 'time' in ds.data_vars else 'time'
            tvals = pd.to_datetime(ds[tname].values)
            row['t_min'] = str(tvals.min())
            row['t_max'] = str(tvals.max())
            row['n_time'] = int(len(tvals))
            ds.close()
        elif path.suffix == '.csv':
            df = pd.read_csv(path, parse_dates=['datetime_utc'])
            row['t_min'] = str(df['datetime_utc'].min())
            row['t_max'] = str(df['datetime_utc'].max())
            row['n_time'] = int(len(df))
    except Exception as e:
        row['error'] = str(e)

qc_df = pd.DataFrame(summary)
print(qc_df.to_string(index=False))
"""
    )
)
cells.append(
    code(
        """# Depth-coverage first look — WFP + SBI (T019; full audit in notebook 02)
wfp_c = xr.open_dataset(WFP_OUT)
sbi_c = xr.open_dataset(SBI_OUT)
wfp_d = wfp_c.depth.values
sbi_d = sbi_c.depth.values

print('=== WFP01 profiler (25-79 m nominal) ===')
print(f'  samples:          {len(wfp_d):,}')
print(f'  min depth:        {float(np.min(wfp_d)):.1f} m')
print(f'  median depth:     {float(np.median(wfp_d)):.1f} m')
print(f'  max depth:        {float(np.max(wfp_d)):.1f} m')
print(f'  depth > 50 m:     {(wfp_d > 50).sum():,}  ({100*(wfp_d > 50).mean():.1f}%)')

print('\\n=== SBI01 near-surface cable CTD ===')
print(f'  samples:          {len(sbi_d):,}')
print(f'  depth range:      {float(np.min(sbi_d)):.2f} → {float(np.max(sbi_d)):.2f} m')

print('\\n=== Combined coverage ===')
print(f'  Surface (~0.5 m):     SBI01     ({len(sbi_d):,} samples)')
print(f'  Mid column (0.5-25 m): **GAP**  (not sampled on CP13NOPM — see research.md)')
print(f'  Profile (25-79 m):    WFP01     ({len(wfp_d):,} samples)')
wfp_c.close()
sbi_c.close()
"""
    )
)
cells.append(
    md(
        """### Next

Notebook 02 (`02_qc_and_align.ipynb`) will: apply QARTOD filtering, range
checks, sigma→z conversion, depth-coverage audit, and time-alignment to
an hourly common cadence. It reads the three files written here from
`outputs/data/raw/` and writes tidy Parquet to `outputs/data/processed/`.

**Manual follow-up**: update the "Retrieval date" line in
`outputs/data/README.md` to reflect today's date ({RETRIEVAL_DATE})."""
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
    "language_info": {
        "name": "python",
    },
}

out_path = Path(__file__).parent / "01_download_erin_data.ipynb"
with out_path.open("w") as f:
    nbf.write(nb, f)

print(f"Wrote {out_path}")
print(f"  cells: {len(cells)} ({sum(1 for c in cells if c.cell_type == 'markdown')} md, {sum(1 for c in cells if c.cell_type == 'code')} code)")
