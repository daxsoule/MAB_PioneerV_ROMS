# `outputs/data/` — Data Provenance

This directory holds project-local copies and derived products of the
data used in spec 001. Raw files are gitignored (see project
`.gitignore`); this README is the version-controlled record of where
everything came from.

## Spec 001 — Hurricane Erin (2025) × MAB South × DOPPIO

**Event window**: 2025-08-15 to 2025-08-29 (UTC).
**Closest approach**: 2025-08-21 12:00 UTC.

### Observations — OOI Pioneer MAB South profiler CTD

- **Reference designator**: `CP13NOPM-WFP01-03-CTDPFK000`
- **Stream**: `recovered_wfp` (recovered wire-following profiler, QARTOD'd)
- **Source path**: `/home/jovyan/ooi/kdata/CP13NOPM-WFP01-03-CTDPFK000-recovered_wfp-ctdpf_ckl_wfp_instrument_recovered/`
- **Deployment spanning Erin**:
  `deployment0002_CP13NOPM-WFP01-03-CTDPFK000-recovered_wfp-ctdpf_ckl_wfp_instrument_recovered_20250415T180015-20251106T152833.nc`
- **No download required** — local mirror on JupyterHub.
- **Fallback** if a gap exists in the recovered stream across the
  event: `telemetered` stream at the sibling path.

### Model — Rutgers DOPPIO operational (`2017_da` PSAS forecast system)

- **OPeNDAP URL**: `https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best`
- **Catalog page**: `https://tds.marine.rutgers.edu/thredds/catalog/roms/doppio/catalog.html`
- **Variables**: `temp`, `salt`, plus grid reconstruction fields
  (`Cs_r`, `hc`, `h`, `zeta`, `lon_rho`, `lat_rho`, `s_rho`).
- **Subset strategy**: nearest-neighbour lookup on `lon_rho`/`lat_rho`
  to the CP13N mooring position, then index-based slice around that
  `xi_rho`/`eta_rho` with a small buffer; time slice 2025-08-15 to
  2025-08-29.
- **Retrieval date**: 2026-04-14 (auto-set by notebook 01)
- **Run version**: `2017_da` operational PSAS (Nov 2017 – present).
- **Why not reanalysis?**: DOPPIO V3R3 reanalysis ends 2024; does not
  cover Erin.

### Hurricane track — NOAA NHC Tropical Cyclone Report

- **Source**: https://www.nhc.noaa.gov/data/tcr/AL052025_Erin.pdf
- **Storm ID**: AL052025
- **Issued**: 2026-01-30 (final)
- **License**: US Government public domain.
- **Retrieval**: 6-hourly best-track positions extracted from Table 1
  into `outputs/data/raw/erin_nhc_besttrack.csv`.
- **HURDAT2 availability**: HURDAT2 for the 2025 season is not yet
  released; if it appears at https://www.nhc.noaa.gov/data/hurdat/
  before completion, promote to that source.

### Surface validation reference (informational, not analyzed)

- NDBC buoy 44014 (Virginia Beach, ~36.6°N, 74.8°W) — close to
  MAB South. Recorded min SLP 1001 mb and 34-kt sustained winds at
  2025-08-21 11:00 UTC. Confirms the forcing timing; not part of the
  comparison but a useful sanity check.
