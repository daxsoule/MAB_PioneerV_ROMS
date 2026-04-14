# Research & Phase 0 Decisions — Spec 001

**Spec**: `specs/001-erin-mab-response/spec.md`
**Plan**: `specs/001-erin-mab-response/plan.md`
**Created**: 2026-04-14

This file records the Phase 0 research items and methodological
defaults adopted in the absence of an explicit `/speckit.clarify`
round. Every decision here is reversible — flagged as such where a
sensitivity check is cheap.

---

## Phase 0.1 — Erin (2025) event window

**Decision (default)**: Event window bracketed as roughly two weeks
spanning Hurricane Erin's closest approach to the MAB South array,
with the exact bounds set from the NOAA NHC best-track archive during
notebook 01. Three sub-windows:

- **Pre-storm**: ~5 days ending 24 h before closest approach.
- **Storm**: closest approach ± 24 h.
- **Recovery**: ~7 days starting 24 h after closest approach.

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

## Phase 0.3 — DOPPIO dataset version

**Decision (default)**: Use the most recent DOPPIO operational or
reanalysis product on Rutgers THREDDS that covers the Erin window.
Pin the full OPeNDAP URL, dataset version/identifier, and retrieval
date in `outputs/data/README.md` and in the Stage 1 notebook's first
markdown cell.

**Rationale**: DOPPIO has operational and reanalysis streams with
different data-assimilation cadences; the reanalysis version, when
available, is preferred because it is retrospective and better
quality-controlled. If only operational is available for the event
window, use that and note it.

**Alternatives considered**: Running our own ROMS simulation —
rejected, out of scope for a student demo.

**Reversible?** Yes — switching DOPPIO versions is a URL change in
notebook 01 and a full re-run downstream. Cheap enough to re-run with
a second version as a sensitivity check if time permits.

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
