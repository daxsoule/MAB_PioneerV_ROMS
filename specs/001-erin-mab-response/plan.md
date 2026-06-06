# Analysis Plan: Hurricane Erin (2025) — MAB South T/S Response vs. DOPPIO

**Spec**: `specs/001-erin-mab-response/spec.md`
**Created**: 2026-04-14
**Status**: Draft

## Summary

Compare T/S at OOI Pioneer MAB South profiler mooring
`CP13NOPM-WFP01-03-CTDPFK000` against DOPPIO ROMS output at the nearest
grid cell, across the pre-storm / storm / recovery sub-windows of
Hurricane Erin (2025). Deliverable: four self-contained Jupyter
notebooks that run end-to-end from raw public data to comparison
figures and statistics. Audience is students using the notebooks as a
teaching demo (constitution: Plotly / interactive figure tier).

## Analysis Environment

**Language/Version**: Python 3.12 (per project `.python-version`).

**Key packages** (per notebook, self-contained install cell):
- Core: `xarray`, `numpy`, `pandas`, `netCDF4`
- OOI download: `requests` (M2M API) or direct HTTPS/THREDDS
- ROMS: `xarray` + `dask` for DOPPIO; `gsw` (TEOS-10) for density /
  mixed-layer calculations. Consider `xroms` if sigma-to-z helpers
  are needed.
- Track: simple CSV/JSON reader; optionally `cartopy` for the track
  map.
- Plotting: `plotly` for student-facing notebooks (default);
  `matplotlib` + `cmocean` only if a figure is promoted to a static
  deliverable.
- Testing: `pytest` for any helper code moved to `src/`.

**Environment files**:
- Project-level `pyproject.toml` / `uv.lock` exist and pin the dev
  environment (scripts, tests).
- Notebooks do **not** rely on the project venv — each declares and
  installs its own dependencies with pinned versions in the first code
  cell, per constitution (Colab-compatible).

## Compute Environment

- [x] Laptop / JupyterHub container
- [ ] Shared server
- [ ] HPC cluster
- [ ] Cloud

**Data scale**: Small — a single CTD profiler record over ~2 weeks is
tens of MB; a DOPPIO subset at one grid cell + vertical × 2 weeks is
also small. NHC best-track is KB. Total well under 1 GB. No chunking
required.

**Timeline pressure**: None stated. Exploratory teaching demo.

**Known bottlenecks**: THREDDS/OPeNDAP latency for DOPPIO can be slow
for full-domain queries — mitigate by requesting only the grid cell(s)
and time range we actually need.

## Constitution Check

- [x] Data sources match those defined in constitution (CP13N OOI WFP
      CTD; DOPPIO primary ROMS; NHC track as auxiliary)
- [x] Coordinate systems/units are consistent (WGS84, UTC, °C, dbar,
      PSU); sigma→z conversion planned at preprocessing
- [x] Figure standards will be followed (Plotly default for student
      audience; `timeseries-figure` / `map-figure` rubric applied)
- [x] Quality checks are incorporated (QARTOD 1 or 2 only; hurricane-
      window excursions reviewed case-by-case per constitution)
- [x] Self-contained notebook rule acknowledged (first-cell installs,
      no reliance on project venv)
- [x] AI-generated prose in markdown cells will carry the disclosure
      label per constitution

**Issues to resolve**: None that block the plan. Three Phase 0 research
items below must complete before bulk downloads.

## Project Structure

```text
MAB_PioneerV_ROMS/
├── .specify/memory/constitution.md
├── specs/
│   └── 001-erin-mab-response/
│       ├── spec.md
│       ├── plan.md           ← this file
│       ├── research.md       ← Phase 0 decisions
│       └── tasks.md          ← to be created by /speckit.tasks
├── notebooks/
│   ├── 01_download_erin_data.ipynb
│   ├── 02_qc_and_align.ipynb
│   ├── 03_hovmoller_comparison.ipynb
│   └── 04_mixed_layer_response.ipynb
├── outputs/
│   ├── data/
│   │   ├── raw/              ← immutable downloads (gitignored)
│   │   ├── processed/        ← aligned, QC'd tidy tables (gitignored if large)
│   │   └── README.md         ← provenance: URLs, retrieval dates, versions
│   ├── figures/001-erin-mab-response/
│   └── tables/001-erin-mab-response/
├── src/                      ← helper module for logic that needs pytest coverage
└── tests/
```

**Structure notes**:
- Notebooks are the deliverable. Helper code that is non-trivial and
  would benefit from pytest coverage (sigma→z converter, MLD
  calculator, QARTOD filter) moves to `src/` and is imported by the
  notebooks. Notebooks still install `src/` requirements in their
  first cell so Colab runs work.
- `outputs/data/raw/` and `outputs/data/processed/` hold NetCDF /
  Parquet. Both are gitignored per the existing `.gitignore`.
- Figures and tables are organized by spec number so multiple specs
  can coexist without collisions.

## Data Pipeline

### Phase 0: Research & Confirmation (BEFORE bulk download)

- **Phase 0.1**: ~~Retrieve Erin 2025 NHC best track and define the
  event window~~ **Resolved 2026-04-14**. Event window
  2025-08-15 to 2025-08-29; CPA 2025-08-21 12:00 UTC. Source:
  NHC TCR AL052025_Erin.pdf.
- **Phase 0.2**: ~~Confirm `CP13NOPM-WFP01-03-CTDPFK000` has a
  deployment covering that window~~ **Resolved**: deployment0002 in
  kdata covers 2025-04-15 → 2025-11-06, spanning the whole 2025
  Atlantic hurricane season. Depth-coverage audit still needed at
  the QC/align stage.
- **Phase 0.3**: ~~Pin the DOPPIO dataset URL and version for the event
  window~~ **Resolved 2026-04-14**. Use operational `2017_da` run,
  hourly `History_Best` aggregation:
  `https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best`.
  Reanalysis V3R3 does not cover Aug 2025.

Decisions and alternatives recorded in `research.md`.

### Stage 1: Data Acquisition — `notebooks/01_download_erin_data.ipynb`

**Observations (no download — local mirror available)**:

Two CTD assets on site CP13NOPM, same deployment:

- **WFP01 CTDPFK (profiler)**:
  `/home/jovyan/ooi/kdata/CP13NOPM-WFP01-03-CTDPFK000-recovered_wfp-ctdpf_ckl_wfp_instrument_recovered/`
  deployment0002 aggregate — depth range 25–79 m.
- **SBI01 CTDMOS (near-surface cable CTD)**:
  `/home/jovyan/ooi/kdata/CP13NOPM-SBI01-02-CTDMOS011-recovered_inst-ctdmo_ghqr_instrument_recovered/`
  deployment0002 aggregate — fixed depth ~0.5 m.

Both span 2025-04-15 → 2025-11-06. Read both, subset to the event
window, write separate NetCDF outputs. Depth gap 0.5–25 m is
unsampled on this mooring (documented limitation in spec).

**Fallback**: If recovered stream has a gap around the storm for
either asset, use telemetered with a note.

**Downloads**:

- **NHC TCR** for Erin (AL052025):
  https://www.nhc.noaa.gov/data/tcr/AL052025_Erin.pdf — extract
  6-hourly positions from Table 1 into a simple CSV.
- **DOPPIO hourly subset** from Rutgers operational `2017_da` run:
  `https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best`
  — time slice 2025-08-15 to 2025-08-29, spatial bounding box around
  CP13N (nearest `xi_rho`/`eta_rho` ± a small index buffer), all
  40 `s_rho` levels, variables `temp`, `salt`, and the grid
  reconstruction fields (`Cs_r`, `hc`, `h`, `zeta`, `lon_rho`, `lat_rho`).

**Output**:
- `outputs/data/raw/erin_nhc_besttrack.csv`
- `outputs/data/raw/CP13NOPM_WFP01_03_CTDPFK000_erin.nc`
- `outputs/data/raw/doppio_CP13N_<window>.nc`
- `outputs/data/README.md` updated with the kdata source path, NHC
  retrieval URL + date, and DOPPIO dataset URL + version + date.

### Stage 2: QC & Alignment — `notebooks/02_qc_and_align.ipynb`

- **Input**: raw NetCDF from Stage 1.
- **Processing**:
  - Apply QARTOD flag filter (accept 1 or 2) to observations.
  - Range-check obs against constitution bounds; flag excursions for
    case-by-case review (not silent reject).
  - Audit depth coverage of CP13N deployment; document usable range.
  - DOPPIO: convert sigma→z at CP13N grid cell (via `gsw` or
    `xroms`); select horizontal interpolation per `research.md`.
  - Align both products to a common hourly cadence (average, do not
    upsample).
- **Output**:
  - `outputs/data/processed/obs_CP13N_erin.parquet` (tidy: time,
    depth, T, S, pressure, QC flag).
  - `outputs/data/processed/doppio_CP13N_erin.parquet` (same schema).

### Stage 3: Hovmöller Comparison — `notebooks/03_hovmoller_comparison.ipynb`

- **Input**: processed Parquet from Stage 2.
- **Processing**: Build T(z, t) and S(z, t) for both products on a
  common depth grid; side-by-side Plotly heatmaps with storm-passage
  time annotated.
- **Output**:
  - Figures 1–4 in `outputs/figures/001-erin-mab-response/`.

### Stage 4: Mixed-Layer Response & Stats — `notebooks/04_mixed_layer_response.ipynb`

- **Input**: processed Parquet from Stage 2.
- **Processing**:
  - Compute MLD time series for both products using the criterion
    selected in `research.md`.
  - Compute surface-layer mean T and S time series.
  - Compute bias, RMSE, correlation per sub-window (pre-storm / storm
    / recovery); include sample size N for each.
- **Output**:
  - Figures 5–6 in `outputs/figures/001-erin-mab-response/`.
  - `outputs/tables/001-erin-mab-response/comparison_stats.csv`.
  - `outputs/tables/001-erin-mab-response/data_provenance.csv`.

## Script/Notebook Plan

| Notebook | Purpose | Inputs | Outputs |
|---|---|---|---|
| `01_download_erin_data.ipynb` | Fetch NHC track, OOI CTD, DOPPIO subset | Public URLs/APIs | `outputs/data/raw/*` |
| `02_qc_and_align.ipynb` | QARTOD filter, sigma→z, hourly align | `outputs/data/raw/*` | `outputs/data/processed/*.parquet` |
| `03_hovmoller_comparison.ipynb` | Side-by-side T/S Hovmöllers | `outputs/data/processed/*` | Figures 1–4 |
| `04_mixed_layer_response.ipynb` | MLD + surface T/S + comparison stats | `outputs/data/processed/*` | Figures 5–6, tables |

Optional `src/` module (created if/when logic grows beyond notebook-
comfortable size):

| Module | Purpose |
|---|---|
| `src/sigma_to_z.py` | ROMS sigma → z at a point |
| `src/mld.py` | Mixed-layer depth calculator (criterion per research.md) |
| `src/qc.py` | QARTOD + range-check helpers |

Any logic in `src/` requires pytest coverage before commit per the
constitution's Testing section.

## Dependencies

```text
Phase 0: Erin window ────┐
Phase 0: CP13N deploy ───┼──→ 01_download → 02_qc_align ─┬→ 03_hovmoller → figures 1–4
Phase 0: DOPPIO version ─┘                               └→ 04_mixed_layer → figures 5–6, tables
```

**Sequential**: Phase 0 gates Stage 1; Stage 1 gates Stage 2; Stage 2
gates Stages 3 and 4.

**Parallel opportunities**: Stages 3 and 4 are independent once Stage
2 completes — can run concurrently.

## Open Questions

Resolved in `research.md` with recommended defaults; each default is
reversible and flagged for sensitivity check where cheap.

- [ ] **Erin event window** — Phase 0.1.
- [ ] **CP13N depth coverage** for the Erin deployment — Phase 0.2.
- [ ] **DOPPIO dataset version** for the event window — Phase 0.3.
- [ ] **Mixed-layer depth criterion** — default: de Boyer Montégut
      (2004) density threshold Δσθ = 0.03 kg m⁻³ from a 10 m reference.
- [ ] **DOPPIO → CP13N horizontal interpolation** — default: nearest-
      neighbour on DOPPIO's native curvilinear grid.
- [ ] **OOI stream: recovered vs. telemetered** — default: recovered if
      available; else telemetered with a note.

## Notes

- User bypassed `/speckit.clarify`. Six open questions above are
  resolved with defaults in `research.md` rather than left blank;
  each default is reversible.
- If `CP13NOPM-WFP01-03-CTDPFK000` lacks adequate depth coverage for
  the Erin window, candidate fallbacks (same array, different asset)
  are listed in `research.md` Phase 0.2.
