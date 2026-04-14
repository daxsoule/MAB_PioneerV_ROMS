# MAB Pioneer (Coastal Virginia) & ROMS Model–Observation Comparison Research Constitution

## Research Context

This project compares observations from the OOI Pioneer MAB South
(Coastal Virginia) Array with regional ocean model output (e.g.,
DOPPIO / ESPreSSO / NYB-ROMS). The goal is to evaluate how well
existing ROMS simulations reproduce the Coastal Virginia shelf regime
and where observation–model mismatches point to gaps in forcing,
physics, or sampling.

The active scientific question (specific variables, time windows,
metrics) lives in the project spec. This constitution governs the
standards that apply regardless of the specific question framing.

## Core Principles

### I. Reproducibility

Every result traces to version-controlled code, pinned environments
(`pyproject.toml` / `uv.lock`), and documented data snapshots. Raw
model output and observations are downloaded by scripts with logged
URLs, checksums, and retrieval dates — not hand-curated.

### II. Data Integrity

Raw ROMS output and OOI NetCDF files are immutable. All regridding,
interpolation, and subsetting produces new files in `outputs/data/`,
never overwrites sources. Missing or masked values are preserved as
NaN with a flag column, not silently dropped.

### III. Provenance

Every figure, table, and statistic links back to: the code that
produced it, the input files (including model run ID and deployment
number), and the coregistration method used. Model–observation
comparison plots must identify both datasets explicitly in the caption
(product name, version, time range, vertical level or depth).

### IV. Coregistration Discipline

Model and observation comparisons require explicit decisions about:
- **Time**: matching window, temporal averaging (hourly/daily/monthly),
  lag treatment. Default is to average both products to the coarser
  native cadence rather than interpolate the finer one.
- **Space**: the model grid cell(s) used for a given mooring location,
  how horizontal interpolation was done (nearest / bilinear), and how
  land masking / wet-point checks were handled.
- **Depth**: how model sigma levels were mapped to observation depths
  (e.g., linear in z, pressure-based). State assumptions explicitly.
- **Variable identity**: potential vs. in-situ temperature, practical
  vs. absolute salinity, pressure vs. depth. Convert before comparing;
  do not assume equivalence.

### V. Model Humility

ROMS output is a simulation, not truth. Observation–model differences
are not automatically model errors — they can reflect observation
representativeness, unresolved processes, spin-up, open-boundary
forcing, or simply a different realization of turbulence. Discuss
mismatches as hypotheses to investigate, not as corrections to apply
to the model.

### VI. Honest Framing

State what this project can and cannot conclude. A single mooring
evaluated against a regional model constrains some statistics (seasonal
cycle, mean stratification, event response) and cannot constrain others
(mesoscale eddy statistics, basin-wide heat budgets). Make those
boundaries explicit in abstracts, captions, and READMEs.

## Data Sources

### OOI Pioneer MAB South / Coastal Virginia Array (2024–present)

- **Description**: OOI Coastal & Global Scale Node array relocated
  from New England to the Mid-Atlantic Bight south of the Chesapeake
  Bay shelf break (~37°N, 75°W region). Surface moorings, profiler
  moorings, and gliders spanning inner shelf to slope.
- **Access**: OOI Data Explorer (https://dataexplorer.oceanobservatories.org/),
  OOINet / M2M API, and — where mirrored — `/home/jovyan/ooi/kdata/`.
- **Temporal coverage**: Deployments starting 2024; treat as an
  actively growing record.
- **Key variables**: temperature, salinity, pressure, velocity, optical
  backscatter, fluorescence (platform-dependent).
- **Known issues**: New array — telemetered vs. recovered stream
  availability varies; deployment-to-deployment depth coverage must be
  audited (per CP02PMUO lesson); QARTOD flags still maturing for some
  instruments.
- **Documentation**: https://oceanobservatories.org/array/coastal-pioneer-mab/

### Regional ROMS products

- **DOPPIO** (Rutgers, MAB/GoM): https://tds.marine.rutgers.edu/
- **ESPreSSO / NYB-ROMS** and successors as they appear.
- **Access**: THREDDS/OPeNDAP where public; document the exact dataset
  URL, version, and retrieval date in `outputs/data/README.md` and in
  any downloader script.
- **Known issues**: Spin-up periods, open-boundary artifacts near the
  domain edges, vertical sigma coordinate must be converted to z for
  comparison, land mask vs. wet-cell mismatches.

## Technical Environment

- **Language**: Python ≥3.12 (JupyterHub environment)
- **Package management**: `uv` (use `uv add`, not `pip install`)
- **Key packages**: xarray, pandas, numpy, netCDF4, matplotlib
  (publication), plotly (exploratory), and ROMS-specific helpers
  (`xroms` or equivalent) added as the work requires them.
- **Compute environment**: JupyterHub container (CPU-capped; 24-worker
  ceiling for parallel jobs per user's global rule).
- **Version control**: Git. Raw data stays outside the repo; processed
  slices in `outputs/data/` (large files gitignored).

## Coordinate Systems & Units

- **Spatial reference**: WGS84 (EPSG:4326) for lat/lon. ROMS grids are
  curvilinear — document which horizontal interpolation method is used
  to get to observation locations.
- **Vertical**: ROMS native sigma; convert to depth (m) or pressure
  (dbar) explicitly before comparison.
- **Time zone**: UTC.
- **Standard units**: °C, dbar, PSU (practical salinity), m/s.
- **Missing data**: NaN.

## Figure Standards

- **Exploratory / notebook figures**: Plotly (interactive, hover, zoom).
- **Publication figures**: Matplotlib, 300 dpi PNG or PDF vector.
- **Colormaps**: Colorblind-safe (`viridis`, `cividis`, `cmocean.thermal`,
  Okabe-Ito for categorical).
- **Comparison plots**: Always label which product is which; use
  consistent color assignments across figures (e.g., observations in
  black, model in a sequential color).
- **Rubrics**: Score every figure against `timeseries-figure` or
  `map-figure` rubric before committing. Paper tier by default.

## Quality Checks

- **Observations**:
  - QARTOD flags: accept only flag=1 (pass) or 2 (not evaluated).
  - Range checks (MAB shelf/slope bounds):
    - Temperature: 2–28 °C
    - Salinity: 28–37 PSU
    - Pressure: 0–500 dbar
- **Model**:
  - Respect the land/wet mask; do not compare at masked cells.
  - Exclude documented spin-up window and open-boundary buffer cells.
- **Comparison**:
  - Match units and variable identity before taking differences.
  - Report sample size for every comparison statistic.

## AI Authorship & Disclosure

All AI-generated prose (methods text, notebook markdown cells, READMEs,
figure captions, report drafts) carries the standard italic disclosure
label at the top and renders in Courier New monospace per the user's
global AI-disclosure rule. Code, code comments, commit messages,
filenames, and short inline labels are exempt.

## Testing

- `pytest` is mandatory. All non-trivial logic (loaders, regridders,
  coregistration helpers, metric calculators) has tests in `tests/`.
- Code must pass `uv run pytest` before every commit. Do not skip or
  disable failing tests.

## Literature Handling

- Papers live under `literature/{open_access,library_subscription,author_copies,embargoed}/`
  with a README inventory. Targeted `.gitignore`, not blanket `*.pdf`.
- Publisher PDFs (paywalled / author copies) are uploaded by the user.
  Claude does not curl-download outside fully open-access sources
  (CC-BY, PMC, public domain).

## Project Notes

- **Repository visibility**: Public GitHub repo (`daxsoule/MAB_PioneerV_ROMS`).
- **Audience**: Likely to include collaborators and students; keep
  READMEs and notebooks approachable and cite all data sources.
- **Status**: New project as of 2026-04-14. No publication timeline or
  embargo yet.
