# MAB Pioneer (Coastal Virginia) & ROMS Model–Observation Comparison Research Constitution

## Research Context

This project compares observations from the OOI Pioneer MAB South
(Coastal Virginia) Array with regional ocean model output (e.g.,
DOPPIO / ESPreSSO / NYB-ROMS) during a **known hurricane event** that
passed over the array. The goal is to evaluate how both the moored
observations and the ROMS simulation capture the event — its timing,
magnitude, vertical structure, and recovery — and to identify where
model and observations diverge.

Event-scale comparison (rather than seasonal-climatology comparison)
is the primary framing: hurricane passage is a well-defined forcing
that stresses both the observing array and the model, so mismatches
are diagnostic rather than statistical.

The specific hurricane, time window, and metrics live in the project
spec. This constitution governs the standards that apply regardless
of the specific question framing.

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

### DOPPIO (Rutgers MAB/GoM ROMS) — primary model

- **Description**: Rutgers Ocean Modeling Group's data-assimilative
  ROMS simulation covering the Mid-Atlantic Bight and Gulf of Maine.
  The authoritative regional ROMS product for this project.
- **Access**: THREDDS/OPeNDAP at https://tds.marine.rutgers.edu/
  (document the exact dataset URL, version, and retrieval date in
  `outputs/data/README.md` and in any downloader script).
- **Known issues**: Spin-up periods, open-boundary artifacts near
  domain edges, vertical sigma coordinate must be converted to z for
  comparison, land mask vs. wet-cell mismatches, assimilation
  increments can produce timing-specific features.

### Secondary ROMS products (for cross-check only)

- **ESPreSSO** — older MAB ROMS; useful for a second-opinion check
  but not the anchor.
- **NYB-ROMS** — smaller New York Bight domain; include only if a
  given version covers the Pioneer MAB South footprint.
- Do not swap the primary-vs-secondary role without updating the spec.

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
- **Self-contained notebooks**: Every notebook declares and installs
  its own dependencies in the first code cell (e.g., `%pip install
  xarray netCDF4 matplotlib plotly` or equivalent) so it runs
  standalone in a fresh Jupyter / Colab environment without relying
  on the project's `uv` venv. Pin versions in the install cell. The
  project `pyproject.toml` remains the authoritative environment for
  scripts and tests, but notebooks must not assume it.

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

Primary audience is **students** working through the notebooks as a
teaching demo, so figures default to interactive and exploratory.

- **Default (student-facing notebooks)**: Plotly — interactive, hover
  for values, zoom/pan. Every figure should invite exploration.
- **Optional publication export**: If a figure is promoted to a paper
  or static deliverable, re-render in matplotlib at 300 dpi PNG or
  PDF vector.
- **Colormaps**: Colorblind-safe (`viridis`, `cividis`,
  `cmocean.thermal`, Okabe-Ito for categorical).
- **Comparison plots**: Always label which product is which; use
  consistent color assignments across figures (e.g., observations in
  black, DOPPIO in a sequential color).
- **Rubrics**: Score every figure against `timeseries-figure` or
  `map-figure` rubric before committing. Student-lab tier: clarity
  and pedagogy first; paper tier only when exporting a final figure.
- **Captions**: Write for a student reader — say what the figure
  shows and why it matters, not just the axes.

## Quality Checks

- **Observations**:
  - QARTOD flags: accept only flag=1 (pass) or 2 (not evaluated).
  - Range checks (typical MAB shelf/slope bounds):
    - Temperature: 2–28 °C
    - Salinity: 28–37 PSU
    - Pressure: 0–500 dbar
  - **Hurricane-event excursions**: The bounds above are intentionally
    set for typical conditions. Real storm effects (rapid surface
    cooling from mixing, freshening from rain/runoff, surge at the
    surface mooring) can legitimately push values outside these
    bounds. Flagged excursions during the event window must be
    **reviewed case-by-case**, not silently accepted or rejected.
    This is a teaching feature: students see the QC system fire and
    investigate whether the flag reflects an instrument problem or
    a real oceanographic signal.
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
- **Primary audience**: Students using the notebooks as a teaching
  demo. READMEs, notebook prose, captions, and choice of
  exploratory vs. static figures should all serve that audience
  first. Research outputs (figures, tables) can be promoted later if
  the work becomes publication-ready.
- **Status**: New project as of 2026-04-14. No publication timeline or
  embargo yet.
- **Focal event**: A 2025 hurricane passage over the Pioneer MAB South
  array. Storm name, track, and exact event window TBD in the spec.
