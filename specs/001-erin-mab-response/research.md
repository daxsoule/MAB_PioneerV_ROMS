# Research & Phase 0 Decisions — Spec 001

**Spec**: `specs/001-erin-mab-response/spec.md`
**Plan**: `specs/001-erin-mab-response/plan.md`
**Created**: 2026-04-14

This file records the Phase 0 research items and methodological
defaults adopted in the absence of an explicit `/speckit.clarify`
round. Every decision here is reversible — flagged as such where a
sensitivity check is cheap.

---

## Phase 0.1 — Erin (2025) event window — RESOLVED 2026-04-14

**Status**: Resolved from NHC TCR AL052025_Erin.pdf (issued 2026-01-30).

**Erin life cycle**:
- Genesis 2025-08-11 (Cabo Verde hurricane).
- Cat 5 peak 2025-08-16 18:00 UTC (140 kt, 913 mb).
- **Closest approach to MAB South** (~37°N, 75°W): **2025-08-21
  12:00 UTC** at 34.9°N, 71.7°W — 378 km / 204 nmi SE of the array.
- Cat 2 at CPA (90 kt, 949 mb).
- Became extratropical 2025-08-22 18:00 UTC north of CPA point.
- Merged with extratropical low ~2025-08-28.
- NDBC buoy 44014 (Virginia Beach, ~36.6°N, 74.8°W — close to MAB
  South) recorded min SLP 1001 mb at 2025-08-21 11:00 UTC with
  34-kt sustained winds. Useful sanity check for forcing.

**Event window (decided)**: 2025-08-15 to 2025-08-29 (14 days).

- **Pre-storm**: 2025-08-15 to 2025-08-20 (5 days ending 24 h before CPA).
- **Storm**: 2025-08-20 to 2025-08-22 (CPA ± 24 h).
- **Recovery**: 2025-08-22 to 2025-08-29 (7 days post-storm).

**Rationale**: 24 h around closest approach captures the surface-
forced mixing response at a fixed mooring without bleeding into
recovery dynamics. Five days pre-storm is enough for a baseline that
isn't dominated by antecedent weather. Seven days recovery gives
time for re-stratification to begin.

**Alternatives considered**: Tighter (±12 h storm) — rejected because
CP13N is on a profiler that samples on a ~hour timescale and the
inertial response can lag; wider (±48 h) — rejected because it risks
folding in secondary events.

**Reversible?** Yes — changing sub-window bounds is a 2-line edit in
notebook 02 and re-runs downstream in seconds.

---

## Phase 0.2 — CP13N deployment coverage

**Status update (2026-04-14)**: Local kdata inspection resolved the
deployment question without a round-trip to OOI Data Explorer. The
deployment0002 aggregate NetCDF of the recovered wire-following
profiler stream spans **2025-04-15 → 2025-11-06** — the entire 2025
Atlantic hurricane season. So Erin is covered by a recovered (i.e.,
post-deployment, calibrated, QARTOD'd) stream.

**Decision (default)**: Read deployment0002 from
`/home/jovyan/ooi/kdata/CP13NOPM-WFP01-03-CTDPFK000-recovered_wfp-ctdpf_ckl_wfp_instrument_recovered/`
directly. The depth-coverage audit still runs in notebook 02 before
downstream stages — the deployment being long does not guarantee
surface → ≥50 m coverage at every profile.

**Fallback plan** if the audit fails (depth range too shallow or too
gappy):

1. Try the same reference designator under a different deployment that
   overlaps the event window.
2. Substitute a neighbouring CP13 asset at the same site (surface-
   mooring CTD for surface-only, or the glider if one was present).
3. As a last resort, switch to a different MAB South profiler site —
   requires user confirmation because the "site CP13N" scope choice
   then changes.

**Reversible?** Fallback 1 is cheap. Fallbacks 2 and 3 change the
scope and require the user to re-approve the spec.

---

## Phase 0.3 — DOPPIO dataset version — RESOLVED 2026-04-14

**Status**: Resolved from Rutgers THREDDS catalog probe.

**DOPPIO runs on Rutgers THREDDS**:
- Reanalysis **V3R3** (`DopAnV3R3-ini2007`): 2007–**2024**. Does
  **not** cover Aug 2025 — cannot use for Erin.
- Reanalysis V2R3 (`DopAnV2R3-ini2007`): 2007–2020 (older, too short).
- Operational **`2017_da`** (Real-Time PSAS Forecast System):
  Nov 2017 – present, daily forecast cycles with rolling "Best"
  aggregation. **This is the run for Erin.**

**Decision**: Use operational `2017_da` run.

- **Hourly history (primary)**:
  `https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best`
- **Daily averages (alternative)**:
  `https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/avg/Best_Excluding_Day1`
  (drops day-1 forecast in favour of analysis/nowcast — slightly
  cleaner for retrospective comparison).

**Variables**: `temp`, `salt` (ROMS standard). 40 sigma levels at
rho-points (`s_rho=0..39`); `Cs_r`, `Cs_w`, `hc`, `h`, `zeta` needed
to reconstruct z. Curvilinear C-grid with `lon_rho`, `lat_rho`;
subset by `xi_rho`/`eta_rho` indices after nearest-neighbour lookup,
not by lon/lat slicing.

**Access**: public OPeNDAP, no authentication.

**Caveat**: Operational runs include data-assimilation increments
(per the constitution's Model Humility principle). Increments may
produce discrete step-like features in the time series — flag but do
not "fix."

**Reversible?** Yes — switching to daily `Best_Excluding_Day1` is a
URL change. If the operational hourly has an unexpected gap across
the Erin window, the daily is the immediate fallback.

---

## Phase 0.4 — Mixed-layer depth criterion

**Decision (default)**: de Boyer Montégut et al. (2004) density-
threshold criterion:

> MLD is the depth at which the potential density (σθ) differs from
> σθ at a 10 m reference depth by Δσθ = 0.03 kg m⁻³.

Computed with `gsw` (TEOS-10) potential density from in-situ T and
practical salinity on a common depth grid.

**Rationale**: Density-threshold is the standard for shelf work where
both temperature and salinity contribute to stratification.
de Boyer Montégut's thresholds are the most widely-cited convention
and match what DOPPIO post-processing often reports.

**Alternatives considered**:
- Temperature threshold ΔT = 0.2 °C from 10 m ref — simpler,
  more teachable for a student demo. Useful as a sensitivity check.
- Gradient-based (Kara et al. 2000) — less robust during storm
  passage when the profile is noisy.

**Reversible?** Yes — swapping criteria is a helper-function change.
Plan to compute both Δσθ = 0.03 and ΔT = 0.2 as a sensitivity check
and show the student reader how they differ.

---

## Phase 0.5 — DOPPIO → CP13N horizontal interpolation

**Decision (default)**: Nearest-neighbour on DOPPIO's native
curvilinear rho-point grid, using the rho-point whose lat/lon is
closest to the CP13N mooring position.

**Rationale**: Nearest-neighbour avoids introducing model grid
smoothing into the comparison — the point we're comparing to is the
actual modelled value at a real grid cell, not a synthetic average.
For a teaching demo, this is also the most intuitive choice.

**Alternatives considered**:
- Bilinear interpolation on rho-points — slightly smoother time
  series, but averages over a region that includes grid cells the
  mooring is not at. Can be done as a cross-check.
- Interpolation on the u/v-point grids — only relevant if velocity is
  added in a future spec.

**Reversible?** Yes. Plan to compute the bilinear version in parallel
and report the difference as a sensitivity-check table in Stage 4.

---

## Phase 0.6 — OOI stream: recovered vs. telemetered

**Decision (default)**: Prefer `recovered_wfp` (recovered wire-
following profiler) stream if available covering the full Erin window.
Else use `telemetered` with a note in `outputs/data/README.md`.

**Rationale**: Recovered data are post-deployment, fully-calibrated,
and QARTOD'd. Telemetered data are real-time and less mature.

**Reversible?** Trivially — change the stream label in notebook 01.

---

## Deferred to a future spec / pass

- **Bilinear interpolation sensitivity check** (from Phase 0.5). The
  nearest-neighbour choice stands for spec 001. Bilinear was
  originally planned as a parallel cross-check but is **deferred** —
  not a required task. Revisit when spec 001 is complete, or when a
  reviewer asks whether the comparison is sensitive to the horizontal
  interpolation method. Cheap to add: duplicate the DOPPIO extraction
  at T015–T016 with `xesmf` or a manual bilinear, then append a
  column to `comparison_stats.csv`.

## Open items not yet decided

- **Inertial-response analysis**: T/S mixed-layer response is primary;
  whether to also identify near-inertial oscillations (requires
  velocity) is deferred to a future spec.
- **Storm-track co-plotting**: Decided (yes, Figure 1 shows the NHC
  track). Map projection choice (PlateCarree, UTM, or LCC) is deferred
  to the figure-rubric pass in notebook 03.
- **Error bars on MLD**: Whether to propagate instrument uncertainty
  through MLD — deferred; for a student demo, a bootstrap over the
  hourly bin is probably sufficient.

---

## References (to be filled at implementation)

- NOAA NHC Atlantic Hurricane Season 2025 — Erin best-track archive.
- OOI Data Explorer — Coastal Pioneer MAB South array asset catalog.
- de Boyer Montégut et al. (2004) — MLD density-threshold criterion
  (citation inventory to be added to `literature/open_access/` if the
  paper is used beyond a single threshold value; a single threshold
  value is "facts, not expression" and does not require feeding the
  PDF to Claude).
- Rutgers DOPPIO product documentation.
