# Analysis Specification: Hurricane Erin (2025) — MAB South T/S Response vs. DOPPIO

**Directory**: `specs/001-erin-mab-response`
**Created**: 2026-04-14
**Status**: Draft
**Input**: User description (via `/speckit.specify`): "Name it Erin and choice A for scope (for now) and choice A for what we are comparing"

## Research Question(s)

1. **Primary**: How did the upper-water-column temperature and salinity
   structure at one OOI Pioneer MAB South (Coastal Virginia) profiler
   mooring evolve across the passage of Hurricane Erin (2025) — pre-storm,
   storm, and recovery — and how well does the DOPPIO ROMS simulation
   reproduce that evolution at the same location?
2. **Secondary**: Where does the observation–model comparison agree and
   disagree most — in the mixed-layer deepening, in the surface cooling
   amplitude, in the timing of recovery, or in the re-stratification rate?

**Hypothesis**: DOPPIO will capture the bulk mixed-layer deepening and
surface cooling signature of Erin but will likely differ from
observations in the fine vertical structure and in the precise timing
of the mixed-layer response, because data assimilation increments are
discrete and because sub-grid vertical mixing parameterizations are
tuned to climatology rather than to individual storms.

## Data Description

### Primary Data — Observations

- **Source**: OOI Coastal Pioneer MAB South (Coastal Virginia) Array,
  site CP13NOPM (North Offshore Profiler Mooring). **Two CTD assets
  on the same mooring, same deployment**:
  - **`CP13NOPM-WFP01-03-CTDPFK000`** — wire-following profiler CTD.
    Depth-resolved **25–79 m** (top bumper well below surface by
    mechanical design).
  - **`CP13NOPM-SBI01-02-CTDMOS011`** — cable-mounted near-surface
    CTD at **~0.5 m** depth. Single-depth point measurement of
    surface T/S.
  - **Depth gap 0.5–25 m** is unsampled on this mooring — documented
    limitation (see Limitations).
- **Coverage**: **2025-08-15 to 2025-08-29** (14 days). Event anchor is
  Erin's closest approach at **2025-08-21 12:00 UTC** (~316 km SE of
  the array, Cat 2 at CPA, storm ID AL052025). Pre-storm buffer
  2025-08-15 to 2025-08-20; storm 2025-08-20 to 2025-08-22; recovery
  2025-08-22 to 2025-08-29.
- **Format**: NetCDF from OOI Data Explorer / M2M API; recovered-
  instrument stream preferred over telemetered if timing allows, else
  telemetered with a note.
- **Access**: Local mirror at
  `/home/jovyan/ooi/kdata/CP13NOPM-WFP01-03-CTDPFK000-recovered_wfp-ctdpf_ckl_wfp_instrument_recovered/`
  — deployment0002 aggregate covers 2025-04-15 → 2025-11-06 (full
  2025 Atlantic hurricane season). **No download required.**
  Fallback to OOI Data Explorer
  (https://dataexplorer.oceanobservatories.org/) only if the kdata
  mirror is unavailable or the deployment is replaced.
- **Known issues**:
  - Array is new — QARTOD flags still maturing for some instruments.
  - Depth coverage varies by deployment (apply the CP02PMUO lesson:
    audit depth stats across deployments before depth-bounded claims).
  - Telemetered vs. recovered streams may differ; document which was used.

### Secondary Data — Model

- **Source**: DOPPIO (Rutgers Ocean Modeling Group MAB/GoM ROMS).
- **Purpose**: The model side of the comparison.
- **Coverage**: Same time window as observations, subset to the grid
  cell nearest the focal mooring (with an explicit horizontal
  interpolation choice — nearest vs. bilinear — documented in code).
- **Access**: THREDDS/OPeNDAP at https://tds.marine.rutgers.edu/
  (exact dataset URL, version, and retrieval date logged in
  `outputs/data/README.md` and in the download script).
- **Known issues**: ROMS sigma vertical coordinate — convert to z
  before comparison; spin-up / open-boundary artifacts (focal site is
  interior to the domain, so this should be a minor concern); data-
  assimilation increments may produce discrete features in time series.

### Tertiary Data — Storm Track

- **Source**: NOAA NHC Tropical Cyclone Report for Hurricane Erin
  (AL052025): https://www.nhc.noaa.gov/data/tcr/AL052025_Erin.pdf
  (final, issued 2026-01-30). HURDAT2 for 2025 not yet released;
  use TCR Table 1 6-hourly best-track positions until HURDAT2
  appears at https://www.nhc.noaa.gov/data/hurdat/.
- **Purpose**: Define the event window (closest approach to the focal
  mooring ± pre-storm and recovery buffers); sanity-check forcing.
- **Access**: NHC public archive (CSV/KML). Downloaded by script with
  retrieval date logged.
- **Known issues**: Best track is post-season; if working from
  operational advisories the values may differ.

## Methods Overview

1. **Data preparation**:
   - Read observations for the focal mooring from the local kdata
     mirror and subset to the event window.
   - Download DOPPIO output for the same window + a buffer from
     Rutgers THREDDS/OPeNDAP.
   - Audit the observation record's depth coverage across the deployment(s)
     that span the event; document the usable depth range.
   - Convert DOPPIO sigma → z at the mooring location; select the grid
     cell nearest the mooring (horizontal interpolation choice documented).
   - Align time bases to UTC; average both products to a common cadence
     (default: hourly) rather than interpolating the finer onto the coarser.
   - Unit and variable-identity check before any differencing (in-situ T,
     practical salinity, pressure → depth conversion).

2. **Analysis approach**:
   - Define three sub-windows from the NHC track: **pre-storm** (stable
     baseline), **storm** (closest approach ± ~24 h), and **recovery**
     (returning toward baseline).
   - For observations and model separately:
     - Plot T(z, t) and S(z, t) as Hovmöller diagrams.
     - Compute a mixed-layer depth time series (density or temperature
       threshold; choice documented).
     - Extract surface-layer mean T and S time series.
   - Side-by-side visual comparison of obs and DOPPIO Hovmöllers and
     mixed-layer depth time series.
   - Simple quantitative comparison: bias, RMSE, and correlation on
     surface T and S and on mixed-layer depth for each sub-window.

3. **Validation**:
   - Observation QARTOD flags filtered per constitution (accept 1 or 2).
   - Hurricane-window range-check excursions reviewed case-by-case per
     constitution.
   - Comparison to the Erin NHC track (closest approach time and
     distance) — surface cooling and mixed-layer deepening should be
     concentrated near that time.

**Justification**: Hurricane passage is a well-defined forcing event
that produces a large, predictable signature (deep mixing, surface
cooling) in T/S. A single focal mooring plus the nearest DOPPIO grid
cell is the minimum viable comparison unit. Starting here before
scaling to transects or multiple moorings respects the student-demo
audience and keeps the first spec simple.

## Expected Outputs

### Notebooks (self-contained, per constitution)

- `notebooks/01_download_erin_data.ipynb` — reads observations from
  local kdata; downloads DOPPIO slice and NHC track. Installs its own
  dependencies; writes raw files to `outputs/data/raw/`.
- `notebooks/02_qc_and_align.ipynb` — QARTOD filtering, sigma→z
  conversion, time alignment, usable-depth audit. Writes tidy
  Parquet/NetCDF to `outputs/data/processed/`.
- `notebooks/03_hovmoller_comparison.ipynb` — side-by-side Hovmöller
  diagrams (obs vs. DOPPIO) with storm-passage time annotated.
- `notebooks/04_mixed_layer_response.ipynb` — mixed-layer depth time
  series, surface T/S time series, bias/RMSE/correlation tables per
  sub-window.

### Figures (Plotly-first, per constitution)

- **Figure 1**: Storm track map — Erin's path (NHC) with MAB South
  array annotated; closest approach marked.
- **Figure 2**: Observation Hovmöller — T(z, t) at focal mooring
  across the event window, with storm-passage time marked.
- **Figure 3**: DOPPIO Hovmöller — same variable, same window, same
  location (nearest grid cell).
- **Figure 4**: Side-by-side obs vs. DOPPIO panels for T and for S,
  same color scale, with storm-passage time marked.
- **Figure 5**: Mixed-layer depth time series, obs vs. DOPPIO, with
  sub-window shading (pre-storm / storm / recovery).
- **Figure 6**: Surface T and S time series, obs vs. DOPPIO.

### Tables

- **Table 1**: Comparison statistics (bias, RMSE, correlation) for
  surface T, surface S, and mixed-layer depth, split by sub-window.
- **Table 2**: Data provenance — exact OOI reference designator,
  DOPPIO dataset URL and version, NHC track retrieval date.

### Key Metrics

- Pre-storm vs. storm vs. recovery: surface-layer cooling magnitude (K),
  salinity change (PSU), mixed-layer depth change (m) — obs and DOPPIO.

## Validation Approach

- **Range**: T and S values outside the constitution's typical bounds
  during the event window are reviewed case-by-case, not silently
  rejected (pedagogical feature).
- **Timing consistency**: Peak observed cooling and mixed-layer
  deepening should align (within a few hours) with Erin's closest
  approach per NHC track.
- **Sign of response**: Expect surface cooling and mixed-layer
  deepening; a warming or shoaling response at the focal mooring is a
  red flag to investigate, not a number to publish.
- **Sample size reported**: Every comparison statistic must state N.

## Completion Criteria

- [x] Focal mooring reference designator identified: `CP13NOPM-WFP01-03-CTDPFK000`.
- [ ] Deployment covering Erin's passage confirmed; depth coverage
      audited (needs surface to at least ~50 m for a mixed-layer analysis).
- [ ] DOPPIO dataset URL and time slice identified and downloaded.
- [ ] Erin NHC best-track downloaded and event sub-windows defined.
- [ ] All four notebooks run end-to-end from raw downloads to figures.
- [ ] All figures reproducible from `outputs/data/processed/`.
- [ ] Comparison statistics table generated and reviewed.
- [ ] Provenance table complete (reference designator, DOPPIO URL +
      version, retrieval dates, NHC track file).
- [ ] QC excursions during storm window reviewed and documented.
- [ ] AI-generated prose in notebook markdown cells carries the
      standard disclosure label (per constitution).
- [ ] pytest passing for any helper code moved out of notebooks.
- [ ] Results reproducible from raw data.

## Assumptions & Limitations

**Resolved context** (was assumption; now confirmed from NHC TCR
AL052025, commit `52eeff5`):
- Hurricane Erin (2025) passed ~316 km SE of the MAB South array at
  2025-08-21 12:00 UTC as a Cat 2 (90 kt / 949 mb). A measurable T/S
  response is expected given the very large wind field reported in
  the TCR; the magnitude at CP13N is what this analysis quantifies.

**Assumptions**:
- The focal mooring chosen is a profiler mooring capable of resolving
  the upper-water-column vertical structure needed for a mixed-layer
  analysis. Surface-only moorings are insufficient.
- DOPPIO output covering the Erin window is publicly available on
  THREDDS.
- A single mooring plus the nearest DOPPIO grid cell is sufficient to
  answer the question at this stage. Horizontal variability is out of
  scope for spec 001 (may be revisited in a future spec).

**Limitations**:
- **Observation gap 0.5–25 m**: CP13NOPM samples the near-surface
  (SBI01 at ~0.5 m) and the subsurface column (WFP01 at 25–79 m)
  but not the 0.5–25 m layer in between. Pre-storm mixed-layer depth
  (typically ~5–15 m in MAB summer) may fall entirely within this gap.
  Mixed-layer deepening past 25 m is resolved; shallower dynamics are
  inferred from surface T/S only.
- One mooring does not constrain horizontal structure of the response.
- Model–observation disagreements are hypotheses, not corrections —
  per the constitution's "Model Humility" principle.
- Data-assimilation increments in DOPPIO can introduce timing-specific
  features that are not physical; flag but do not fix.
- Student-lab tier figures; paper-tier export is out of scope for
  this spec.

## Notes

- Constitution alignment checked: data sources (OOI Pioneer MAB South,
  DOPPIO) match the constitution's definitions; coordinate systems /
  units (WGS84, UTC, °C, dbar, PSU) consistent; figure standards
  (Plotly student-first) consistent; QC rules (QARTOD 1 or 2, case-
  by-case storm review) consistent; self-contained notebook rule
  acknowledged.
## Post-analysis note (added 2026-04-14)

Erin's closest approach to CP13NOPM was ~316 km SE — well outside the
inner wind field. The storm affected the MAB South region through its
large peripheral wind field and surge, not through direct over-mooring
passage. Consequences:

- The **direct** wind-mixing signal at the mooring is modest; the
  observed mixed layer does not deepen dramatically past the 25 m WFP
  floor during the storm sub-window.
- Peak surface cooling occurs ~3 days **after** CPA in both obs and
  DOPPIO (see `outputs/tables/001-erin-mab-response/event_timing.csv`).
- This is a **grazing event**, not a direct hit. The primary
  scientific content of spec 001 is therefore about **shelf-scale
  post-storm response** rather than the classic eye-passage signature.
- The spec's original hypothesis (lines 19–24) was implicitly written
  for a closer pass; it remains a valid framing for spec 002 / future
  direct-hit analyses, but should not be over-read against the Erin
  results.

## Original Phase 0 clarifications

- Phase 0 clarifications (resolved unless noted):
  - ~~Which exact MAB South reference designator is the focal mooring?~~
    **Resolved 2026-04-14: `CP13NOPM-WFP01-03-CTDPFK000`.**
  - ~~DOPPIO dataset version/URL for the Erin window.~~
    **Resolved 2026-04-14: operational `2017_da` run,
    `History_Best` hourly aggregation on Rutgers THREDDS
    (see `research.md` Phase 0.3 and `outputs/data/README.md`).**
  - **Deferred to QC stage**: does the CP13N deployment spanning Erin
    have adequate depth coverage for a mixed-layer analysis (surface
    → ≥50 m)? Audited in `notebooks/02_qc_and_align.ipynb`
    (tasks T019, T023).
# Analysis Specification: Hurricane Erin (2025) — MAB South T/S Response vs. DOPPIO

**Directory**: `specs/001-erin-mab-response`
**Created**: 2026-04-14
**Status**: Draft
**Input**: User description (via `/speckit.specify`): "Name it Erin and choice A for scope (for now) and choice A for what we are comparing"

## Research Question(s)

1. **Primary**: How did the upper-water-column temperature and salinity
   structure at one OOI Pioneer MAB South (Coastal Virginia) profiler
   mooring evolve across the passage of Hurricane Erin (2025) — pre-storm,
   storm, and recovery — and how well does the DOPPIO ROMS simulation
   reproduce that evolution at the same location?
2. **Secondary**: Where does the observation–model comparison agree and
   disagree most — in the mixed-layer deepening, in the surface cooling
   amplitude, in the timing of recovery, or in the re-stratification rate?

**Hypothesis**: DOPPIO will capture the bulk mixed-layer deepening and
surface cooling signature of Erin but will likely differ from
observations in the fine vertical structure and in the precise timing
of the mixed-layer response, because data assimilation increments are
discrete and because sub-grid vertical mixing parameterizations are
tuned to climatology rather than to individual storms.

## Data Description

### Primary Data — Observations

- **Source**: OOI Coastal Pioneer MAB South (Coastal Virginia) Array,
  site CP13NOPM (North Offshore Profiler Mooring). **Two CTD assets
  on the same mooring, same deployment**:
  - **`CP13NOPM-WFP01-03-CTDPFK000`** — wire-following profiler CTD.
    Depth-resolved **25–79 m** (top bumper well below surface by
    mechanical design).
  - **`CP13NOPM-SBI01-02-CTDMOS011`** — cable-mounted near-surface
    CTD at **~0.5 m** depth. Single-depth point measurement of
    surface T/S.
  - **Depth gap 0.5–25 m** is unsampled on this mooring — documented
    limitation (see Limitations).
- **Coverage**: **2025-08-15 to 2025-08-29** (14 days). Event anchor is
  Erin's closest approach at **2025-08-21 12:00 UTC** (~316 km SE of
  the array, Cat 2 at CPA, storm ID AL052025). Pre-storm buffer
  2025-08-15 to 2025-08-20; storm 2025-08-20 to 2025-08-22; recovery
  2025-08-22 to 2025-08-29.
- **Format**: NetCDF from OOI Data Explorer / M2M API; recovered-
  instrument stream preferred over telemetered if timing allows, else
  telemetered with a note.
- **Access**: Local mirror at
  `/home/jovyan/ooi/kdata/CP13NOPM-WFP01-03-CTDPFK000-recovered_wfp-ctdpf_ckl_wfp_instrument_recovered/`
  — deployment0002 aggregate covers 2025-04-15 → 2025-11-06 (full
  2025 Atlantic hurricane season). **No download required.**
  Fallback to OOI Data Explorer
  (https://dataexplorer.oceanobservatories.org/) only if the kdata
  mirror is unavailable or the deployment is replaced.
- **Known issues**:
  - Array is new — QARTOD flags still maturing for some instruments.
  - Depth coverage varies by deployment (apply the CP02PMUO lesson:
    audit depth stats across deployments before depth-bounded claims).
  - Telemetered vs. recovered streams may differ; document which was used.

### Secondary Data — Model

- **Source**: DOPPIO (Rutgers Ocean Modeling Group MAB/GoM ROMS).
- **Purpose**: The model side of the comparison.
- **Coverage**: Same time window as observations, subset to the grid
  cell nearest the focal mooring (with an explicit horizontal
  interpolation choice — nearest vs. bilinear — documented in code).
- **Access**: THREDDS/OPeNDAP at https://tds.marine.rutgers.edu/
  (exact dataset URL, version, and retrieval date logged in
  `outputs/data/README.md` and in the download script).
- **Known issues**: ROMS sigma vertical coordinate — convert to z
  before comparison; spin-up / open-boundary artifacts (focal site is
  interior to the domain, so this should be a minor concern); data-
  assimilation increments may produce discrete features in time series.

### Tertiary Data — Storm Track

- **Source**: NOAA NHC Tropical Cyclone Report for Hurricane Erin
  (AL052025): https://www.nhc.noaa.gov/data/tcr/AL052025_Erin.pdf
  (final, issued 2026-01-30). HURDAT2 for 2025 not yet released;
  use TCR Table 1 6-hourly best-track positions until HURDAT2
  appears at https://www.nhc.noaa.gov/data/hurdat/.
- **Purpose**: Define the event window (closest approach to the focal
  mooring ± pre-storm and recovery buffers); sanity-check forcing.
- **Access**: NHC public archive (CSV/KML). Downloaded by script with
  retrieval date logged.
- **Known issues**: Best track is post-season; if working from
  operational advisories the values may differ.

## Methods Overview

1. **Data preparation**:
   - Read observations for the focal mooring from the local kdata
     mirror and subset to the event window.
   - Download DOPPIO output for the same window + a buffer from
     Rutgers THREDDS/OPeNDAP.
   - Audit the observation record's depth coverage across the deployment(s)
     that span the event; document the usable depth range.
   - Convert DOPPIO sigma → z at the mooring location; select the grid
     cell nearest the mooring (horizontal interpolation choice documented).
   - Align time bases to UTC; average both products to a common cadence
     (default: hourly) rather than interpolating the finer onto the coarser.
   - Unit and variable-identity check before any differencing (in-situ T,
     practical salinity, pressure → depth conversion).

2. **Analysis approach**:
   - Define three sub-windows from the NHC track: **pre-storm** (stable
     baseline), **storm** (closest approach ± ~24 h), and **recovery**
     (returning toward baseline).
   - For observations and model separately:
     - Plot T(z, t) and S(z, t) as Hovmöller diagrams.
     - Compute a mixed-layer depth time series (density or temperature
       threshold; choice documented).
     - Extract surface-layer mean T and S time series.
   - Side-by-side visual comparison of obs and DOPPIO Hovmöllers and
     mixed-layer depth time series.
   - Simple quantitative comparison: bias, RMSE, and correlation on
     surface T and S and on mixed-layer depth for each sub-window.

3. **Validation**:
   - Observation QARTOD flags filtered per constitution (accept 1 or 2).
   - Hurricane-window range-check excursions reviewed case-by-case per
     constitution.
   - Comparison to the Erin NHC track (closest approach time and
     distance) — surface cooling and mixed-layer deepening should be
     concentrated near that time.

**Justification**: Hurricane passage is a well-defined forcing event
that produces a large, predictable signature (deep mixing, surface
cooling) in T/S. A single focal mooring plus the nearest DOPPIO grid
cell is the minimum viable comparison unit. Starting here before
scaling to transects or multiple moorings respects the student-demo
audience and keeps the first spec simple.

## Expected Outputs

### Notebooks (self-contained, per constitution)

- `notebooks/01_download_erin_data.ipynb` — reads observations from
  local kdata; downloads DOPPIO slice and NHC track. Installs its own
  dependencies; writes raw files to `outputs/data/raw/`.
- `notebooks/02_qc_and_align.ipynb` — QARTOD filtering, sigma→z
  conversion, time alignment, usable-depth audit. Writes tidy
  Parquet/NetCDF to `outputs/data/processed/`.
- `notebooks/03_hovmoller_comparison.ipynb` — side-by-side Hovmöller
  diagrams (obs vs. DOPPIO) with storm-passage time annotated.
- `notebooks/04_mixed_layer_response.ipynb` — mixed-layer depth time
  series, surface T/S time series, bias/RMSE/correlation tables per
  sub-window.

### Figures (Plotly-first, per constitution)

- **Figure 1**: Storm track map — Erin's path (NHC) with MAB South
  array annotated; closest approach marked.
- **Figure 2**: Observation Hovmöller — T(z, t) at focal mooring
  across the event window, with storm-passage time marked.
- **Figure 3**: DOPPIO Hovmöller — same variable, same window, same
  location (nearest grid cell).
- **Figure 4**: Side-by-side obs vs. DOPPIO panels for T and for S,
  same color scale, with storm-passage time marked.
- **Figure 5**: Mixed-layer depth time series, obs vs. DOPPIO, with
  sub-window shading (pre-storm / storm / recovery).
- **Figure 6**: Surface T and S time series, obs vs. DOPPIO.

### Tables

- **Table 1**: Comparison statistics (bias, RMSE, correlation) for
  surface T, surface S, and mixed-layer depth, split by sub-window.
- **Table 2**: Data provenance — exact OOI reference designator,
  DOPPIO dataset URL and version, NHC track retrieval date.

### Key Metrics

- Pre-storm vs. storm vs. recovery: surface-layer cooling magnitude (K),
  salinity change (PSU), mixed-layer depth change (m) — obs and DOPPIO.

## Validation Approach

- **Range**: T and S values outside the constitution's typical bounds
  during the event window are reviewed case-by-case, not silently
  rejected (pedagogical feature).
- **Timing consistency**: Peak observed cooling and mixed-layer
  deepening should align (within a few hours) with Erin's closest
  approach per NHC track.
- **Sign of response**: Expect surface cooling and mixed-layer
  deepening; a warming or shoaling response at the focal mooring is a
  red flag to investigate, not a number to publish.
- **Sample size reported**: Every comparison statistic must state N.

## Completion Criteria

- [x] Focal mooring reference designator identified: `CP13NOPM-WFP01-03-CTDPFK000`.
- [ ] Deployment covering Erin's passage confirmed; depth coverage
      audited (needs surface to at least ~50 m for a mixed-layer analysis).
- [ ] DOPPIO dataset URL and time slice identified and downloaded.
- [ ] Erin NHC best-track downloaded and event sub-windows defined.
- [ ] All four notebooks run end-to-end from raw downloads to figures.
- [ ] All figures reproducible from `outputs/data/processed/`.
- [ ] Comparison statistics table generated and reviewed.
- [ ] Provenance table complete (reference designator, DOPPIO URL +
      version, retrieval dates, NHC track file).
- [ ] QC excursions during storm window reviewed and documented.
- [ ] AI-generated prose in notebook markdown cells carries the
      standard disclosure label (per constitution).
- [ ] pytest passing for any helper code moved out of notebooks.
- [ ] Results reproducible from raw data.

## Assumptions & Limitations

**Resolved context** (was assumption; now confirmed from NHC TCR
AL052025, commit `52eeff5`):
- Hurricane Erin (2025) passed ~316 km SE of the MAB South array at
  2025-08-21 12:00 UTC as a Cat 2 (90 kt / 949 mb). A measurable T/S
  response is expected given the very large wind field reported in
  the TCR; the magnitude at CP13N is what this analysis quantifies.

**Assumptions**:
- The focal mooring chosen is a profiler mooring capable of resolving
  the upper-water-column vertical structure needed for a mixed-layer
  analysis. Surface-only moorings are insufficient.
- DOPPIO output covering the Erin window is publicly available on
  THREDDS.
- A single mooring plus the nearest DOPPIO grid cell is sufficient to
  answer the question at this stage. Horizontal variability is out of
  scope for spec 001 (may be revisited in a future spec).

**Limitations**:
- **Observation gap 0.5–25 m**: CP13NOPM samples the near-surface
  (SBI01 at ~0.5 m) and the subsurface column (WFP01 at 25–79 m)
  but not the 0.5–25 m layer in between. Pre-storm mixed-layer depth
  (typically ~5–15 m in MAB summer) may fall entirely within this gap.
  Mixed-layer deepening past 25 m is resolved; shallower dynamics are
  inferred from surface T/S only.
- One mooring does not constrain horizontal structure of the response.
- Model–observation disagreements are hypotheses, not corrections —
  per the constitution's "Model Humility" principle.
- Data-assimilation increments in DOPPIO can introduce timing-specific
  features that are not physical; flag but do not fix.
- Student-lab tier figures; paper-tier export is out of scope for
  this spec.

## Notes

- Constitution alignment checked: data sources (OOI Pioneer MAB South,
  DOPPIO) match the constitution's definitions; coordinate systems /
  units (WGS84, UTC, °C, dbar, PSU) consistent; figure standards
  (Plotly student-first) consistent; QC rules (QARTOD 1 or 2, case-
  by-case storm review) consistent; self-contained notebook rule
  acknowledged.
## Post-analysis note (added 2026-04-14)

Erin's closest approach to CP13NOPM was ~316 km SE — well outside the
inner wind field. The storm affected the MAB South region through its
large peripheral wind field and surge, not through direct over-mooring
passage. Consequences:

- The **direct** wind-mixing signal at the mooring is modest; the
  observed mixed layer does not deepen dramatically past the 25 m WFP
  floor during the storm sub-window.
- Peak surface cooling occurs ~3 days **after** CPA in both obs and
  DOPPIO (see `outputs/tables/001-erin-mab-response/event_timing.csv`).
- This is a **grazing event**, not a direct hit. The primary
  scientific content of spec 001 is therefore about **shelf-scale
  post-storm response** rather than the classic eye-passage signature.
- The spec's original hypothesis (lines 19–24) was implicitly written
  for a closer pass; it remains a valid framing for spec 002 / future
  direct-hit analyses, but should not be over-read against the Erin
  results.

## Original Phase 0 clarifications

- Phase 0 clarifications (resolved unless noted):
  - ~~Which exact MAB South reference designator is the focal mooring?~~
    **Resolved 2026-04-14: `CP13NOPM-WFP01-03-CTDPFK000`.**
  - ~~DOPPIO dataset version/URL for the Erin window.~~
    **Resolved 2026-04-14: operational `2017_da` run,
    `History_Best` hourly aggregation on Rutgers THREDDS
    (see `research.md` Phase 0.3 and `outputs/data/README.md`).**
  - **Deferred to QC stage**: does the CP13N deployment spanning Erin
    have adequate depth coverage for a mixed-layer analysis (surface
    → ≥50 m)? Audited in `notebooks/02_qc_and_align.ipynb`
    (tasks T019, T023).
