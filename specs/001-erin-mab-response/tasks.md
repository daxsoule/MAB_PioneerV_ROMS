---
description: "Task list for spec 001 — Hurricane Erin (2025) MAB South × DOPPIO"
---

# Tasks: Hurricane Erin (2025) — MAB South T/S Response vs. DOPPIO

**Spec**: `specs/001-erin-mab-response/spec.md`
**Plan**: `specs/001-erin-mab-response/plan.md`
**Research**: `specs/001-erin-mab-response/research.md`
**Generated**: 2026-04-14

## Format

- `[ ] T### Action` — each task completable without additional context.
- QC tasks are explicit. Phases are sequential (complete the checkpoint before moving on).
- Notebook-heavy project: most tasks land in `notebooks/` per the constitution's self-contained-notebook rule.

---

## Phase 0: Research (RESOLVED — skip)

All three original open questions are resolved (see `research.md`):

- [x] T001 Phase 0.1: Erin event window (2025-08-15 to 2025-08-29; CPA 2025-08-21 12:00 UTC).
- [x] T002 Phase 0.2: CP13N deployment coverage (deployment0002 covers entire 2025 season; local at `/home/jovyan/ooi/kdata/`).
- [x] T003 Phase 0.3: DOPPIO dataset URL pinned (operational `2017_da`, `History_Best`).

**Checkpoint**: Phase 0 complete. Proceed to Phase 1.

---

## Phase 1: Setup

- [x] T004 Create `notebooks/` directory structure (already exists; empty — confirmed 2026-04-14).
- [x] T005 Create `outputs/figures/001-erin-mab-response/` and `outputs/tables/001-erin-mab-response/` (done 2026-04-14).
- [x] T006 Confirm `.gitignore` blocks `outputs/data/**/*.nc` and `outputs/data/**/*.parquet` — **fixed 2026-04-14**: patterns were `outputs/data/*.nc` (top-level only), widened to `outputs/data/**/*.{nc,zarr,parquet,pdf}` to cover subdirs.
- [x] T007 Notebook format: **plain `.ipynb` only** (no jupytext paired `.py`). Decided 2026-04-14. Recorded in project README.

**Checkpoint**: Directory structure in place; `.gitignore` covers large data; notebook format decision recorded.

---

## Phase 2: Data Acquisition — `notebooks/01_download_erin_data.ipynb`

**Purpose**: Stage 1 of the data pipeline. Read obs from local kdata, download DOPPIO slice, download NHC track.

- [ ] T008 Create `notebooks/01_download_erin_data.ipynb`.
- [ ] T009 First-cell install per constitution: pinned versions of `xarray`, `netCDF4`, `numpy`, `pandas`, `requests`, `pyarrow`, `plotly`. Include the AI-disclosure header in the first markdown cell.
- [x] T010 Open CP13N deployment0002 aggregates from kdata — **both WFP01 CTDPFK (profiler, 25–79 m) and SBI01 CTDMOS (near-surface ~0.5 m)**. Added SBI01 per user 2026-04-14 after T019 revealed WFP does not reach the surface.
- [x] T011 Subset both streams to event window 2025-08-15 to 2025-08-29; write to `outputs/data/raw/CP13NOPM-WFP01-03-CTDPFK000_erin.nc` and `CP13NOPM-SBI01-02-CTDMOS011_erin.nc`.
- [x] T012 Extract CP13N lat/lon from WFP record (same mooring, same for SBI). Recorded in notebook for DOPPIO lookup.
- [ ] T013 Download NHC TCR for Erin (AL052025) to `outputs/data/raw/AL052025_Erin_TCR.pdf`. Extract Table 1 6-hourly positions to `outputs/data/raw/erin_nhc_besttrack.csv` (columns: `datetime_utc, lat, lon, max_wind_kt, min_slp_mb, status`).
- [ ] T014 Open DOPPIO OPeNDAP dataset at `https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best` with `xarray.open_dataset(..., chunks={...})`.
- [ ] T015 Nearest-neighbour lookup on `lon_rho`/`lat_rho` to CP13N position → `(xi0, eta0)`. Subset with a small index buffer (e.g., ±3 cells) and time slice 2025-08-15 to 2025-08-29.
- [ ] T016 Select variables `temp`, `salt`, and grid reconstruction fields `Cs_r`, `hc`, `h`, `zeta`, `lon_rho`, `lat_rho`, `s_rho`. Call `.load()`; write to `outputs/data/raw/doppio_CP13N_erin.nc`.
- [ ] T017 Update `outputs/data/README.md` — fill in the DOPPIO "Retrieval date" line and record the NHC retrieval date.
- [ ] T018 **QC**: Verify all three raw files exist, open without error, and cover the event window (print time ranges, sample counts, and file sizes).
- [ ] T019 **QC**: Confirm CP13N observations include surface and at least ~50 m depth in the Erin window (first pass — full depth audit in Phase 3).

**Checkpoint**: Three raw files in place, all opened and time-range-verified, provenance README updated.

---

## Phase 3: Preprocessing — `notebooks/02_qc_and_align.ipynb`

**Purpose**: Stage 2 of the pipeline. QARTOD filter, range-check, sigma→z, time-align.

- [x] T020 Created `notebooks/02_qc_and_align.ipynb` (source: `_build_notebook_02.py`); first-cell install + AI-disclosure header.
- [x] T021 QARTOD filter applied to WFP and SBI (accept flag 1 or 2).
- [x] T022 Constitution range checks (T: 2–28 °C; S: 28–37 PSU; P: 0–500 dbar) applied. Storm-window excursions collected for review (none triggered in this run; noted as zero rejections).
- [x] T023 Depth-coverage audit — WFP usable 25.0–80.0 m, confirmed ≥50 m coverage; SBI at ~0.5 m.
- [x] T024 WFP regridded to 2 m × hourly grid: `outputs/data/processed/obs_profile_CP13N_erin.parquet` (2,648 cells).
- [x] T025 DOPPIO sigma→z via Vtransform=2 formula; sanity-checked at (eta=3, xi=3): z(k=-1)≈zeta, z(k=0)≈-h.
- [x] T026 Nearest rho-point column extracted at (eta=3, xi=3); per-time `np.interp` onto the common 2 m depth grid.
- [x] T027 Alignment to hourly cadence — WFP binned by floor, DOPPIO source already hourly; times match exactly.
- [x] T028 DOPPIO processed Parquet written: `outputs/data/processed/doppio_profile_CP13N_erin.parquet` (9,436 cells).
- [x] T029 QC alignment check: 117/117 WFP times in DOPPIO intersection; 28/28 depth bins identical.
- [x] T030 Quick-look Hovmöller comparison plot rendered (embedded in notebook).

**Checkpoint**: Both products on identical hourly × 2 m grid; depth audit recorded; storm-window excursions surfaced for review.

---

## Phase 4: Hovmöller Comparison — `notebooks/03_hovmoller_comparison.ipynb`

**Purpose**: Stage 3 of the pipeline. Figures 1–4.

- [x] T031 Created `notebooks/03_hovmoller_comparison.ipynb` (source: `_build_notebook_03.py`).
- [x] T032 Figure 1 — `fig01_storm_track.html` — Erin NHC track, CPA marker, CP13NOPM star, category-colored fixes.
- [x] T033 Figure 2 — `fig02_obs_temp_hovmoller.html` — WFP T(z,t) on 2 m × hourly grid, CPA dashed.
- [x] T034 Figure 3 — `fig03_doppio_temp_hovmoller.html` — DOPPIO T(z,t) at nearest rho-point, same color scale.
- [x] T035 Figure 4 — `fig04_obs_vs_doppio_TS.html` — 4-panel obs/DOPPIO × T/S.
- [ ] T036 Rubric scoring (timeseries-figure / map-figure) — **deferred** pending user review of the four figures.
- [x] T037 QC — all four files exist in `outputs/figures/001-erin-mab-response/`, 4.9–5.2 MB each.

**Checkpoint**: Figures 1–4 generated, rubric-scored, saved.

---

## Phase 5: Mixed-Layer & Comparison Stats — `notebooks/04_mixed_layer_response.ipynb`

**Purpose**: Stage 4 of the pipeline. Figures 5–6 + Tables 1–2.

- [x] T038 Create `notebooks/04_mixed_layer_response.ipynb`; first-cell install + AI-disclosure header. Include `gsw` in the install cell.
- [x] T039 Compute potential density `σθ` for both products using `gsw` from T, S, pressure.
- [x] T040 Compute **MLD** using de Boyer Montégut density threshold (Δσθ = 0.03 kg m⁻³ from a 10 m reference). Implement as a small function — if ≥20 lines, move to `src/mld.py` with a pytest test.
- [x] T041 Compute the ΔT = 0.2 °C MLD as a **sensitivity check** (per research.md); include both series on the MLD plot and note the difference in text.
- [x] T042 Compute surface-layer mean T and S time series (depth-weighted mean over 0 → 10 m).
- [x] T043 Define sub-windows: pre-storm (2025-08-15 → 2025-08-20), storm (2025-08-20 → 2025-08-22), recovery (2025-08-22 → 2025-08-29). Compute bias, RMSE, correlation per sub-window for surface T, surface S, and MLD — include sample size N.
- [x] T044 Generate **Figure 5** — MLD time series, obs vs. DOPPIO, both criteria overlaid, with sub-window shading. Caption.
- [x] T045 Generate **Figure 6** — surface T and S time series, obs vs. DOPPIO, with sub-window shading and CPA marked. Caption.
- [x] T046 Generate **Table 1** — `outputs/tables/001-erin-mab-response/comparison_stats.csv` (columns: `variable, subwindow, bias, rmse, correlation, N`).
- [x] T047 Generate **Table 2** — `outputs/tables/001-erin-mab-response/data_provenance.csv` (obs path, DOPPIO URL + retrieval date, NHC TCR URL, MLD criterion used, alignment cadence).
- [x] T048 **QC**: Peak surface cooling and MLD deepening should align (±a few hours) with CPA (2025-08-21 12:00 UTC). If obs and DOPPIO disagree on timing, document — this is a **result**, not a bug.
- [x] T049 **QC**: Sample sizes ≥ something reasonable (e.g., ≥12 hourly samples per sub-window). Flag any sub-window with insufficient data.
- [x] T050 **QC**: Verify all expected spec outputs are present (6 figures + 2 tables under `outputs/{figures,tables}/001-erin-mab-response/`).

**Checkpoint**: Figures 5–6 and Tables 1–2 generated; comparison timing sanity-checked; all 6 figures + 2 tables in place.

---

## Phase 6: Documentation, Tests, Reproducibility

- [ ] T051 Update project `README.md` with a "Spec 001: Hurricane Erin" section — run order of the four notebooks, data sources, and the short-name branch.
- [ ] T052 Add any helper code extracted to `src/` to the install cell of each notebook (editable install if under active development).
- [ ] T053 Ensure every AI-authored markdown cell carries the standard italic disclosure label per constitution; spot-check all four notebooks.
- [ ] T054 Run `uv run pytest` — must pass; zero broken tests before final commit.
- [ ] T055 End-to-end reproducibility check: delete `outputs/data/processed/` and `outputs/figures/001-erin-mab-response/`; re-run notebooks 02–04 from the raw files; confirm outputs match.
- [ ] T056 Constitution check: Plotly used for all figures (not matplotlib); AI disclosure present; QARTOD + range-check + case-by-case storm excursions documented; no library_subscription content was fed to an AI; outputs cite sources.
- [ ] T057 Score every final figure against the `timeseries-figure` or `map-figure` rubric; commit the scores as a markdown cell at the end of the figure-producing notebook.
- [ ] T058 Open a PR from `001-erin-mab-response` → `main` for review; request review before merge.

**Checkpoint**: Fresh clone can reproduce all outputs; pytest green; constitution check passed; PR open.

---

## Dependencies

```text
Phase 0 (resolved) ─→ Phase 1 (setup) ─→ Phase 2 (acquire) ─→ Phase 3 (QC/align) ─┬→ Phase 4 (Hovmöllers)
                                                                                   └→ Phase 5 (MLD + stats)
                                                                                           ↓
                                                                                   Phase 6 (docs/tests/PR)
```

Phases 4 and 5 are independent once Phase 3 completes — can be done in parallel.

---

## Completion Criteria (from spec.md)

- [ ] CP13NOPM-WFP01-03-CTDPFK000 deployment confirmed to cover Erin.
- [ ] Depth coverage audit passed (surface → ≥50 m).
- [ ] DOPPIO slice downloaded and archived.
- [ ] Erin NHC best-track extracted.
- [ ] All four notebooks run end-to-end.
- [ ] All 6 figures reproducible from `outputs/data/processed/`.
- [ ] Comparison statistics table generated and reviewed.
- [ ] Provenance table complete.
- [ ] QC excursions during storm window reviewed and documented.
- [ ] AI disclosure label on all AI-authored markdown cells.
- [ ] `pytest` passing.
- [ ] Results reproducible from raw data.

---

## Notes

- Commit at the end of each phase (or more frequently). Tag commits with the phase number.
- If a task reveals a new requirement (e.g., a needed helper function that outgrows a notebook cell), **add a task** rather than expanding scope silently.
- QC failures block progression. If depth coverage fails at T023, fall back per `research.md` Phase 0.2 plan rather than forcing a bad analysis.
- Constitution's **Model Humility** principle applies throughout Phases 4–5: disagreements between obs and DOPPIO are hypotheses, not corrections.
