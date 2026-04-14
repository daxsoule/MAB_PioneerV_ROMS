# MAB_PioneerV_ROMS

Model–observation comparison between the **OOI Pioneer MAB South
(Coastal Virginia) Array** and regional **ROMS** ocean model output
(DOPPIO / ESPreSSO / NYB-ROMS and successors).

## Status

Spec 001 (`specs/001-erin-mab-response/`): Hurricane Erin (2025) vs.
DOPPIO — **implementation complete on branch `001-erin-mab-response`**.
Four notebooks, 6 figures, 3 tables, pytest suite (15 tests). Ready
for review.

## Spec 001: Hurricane Erin × MAB South × DOPPIO

**Scientific question**: How did upper-water-column T and S at OOI
profiler mooring `CP13NOPM` evolve across Hurricane Erin (2025), and
how well does the Rutgers DOPPIO operational ROMS reproduce that
evolution? Erin passed ~316 km SE of the mooring on 2025-08-21 12:00
UTC at Cat 2 — a grazing event, not a direct hit.

### Notebook run order

All four notebooks are self-contained (install-cell at top, runnable
in Colab) and must be executed in order:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/01_download_erin_data.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_qc_and_align.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_hovmoller_comparison.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/04_mixed_layer_response.ipynb
```

| Notebook | What it does | Inputs | Outputs |
|---|---|---|---|
| `01_download_erin_data.ipynb` | Reads CP13NOPM WFP + SBI CTD from local kdata; downloads NHC TCR PDF and parses Table 1 with `pdfplumber`; downloads DOPPIO slice via OPeNDAP. | `/home/jovyan/ooi/kdata/` + NHC + Rutgers THREDDS | `outputs/data/raw/*` |
| `02_qc_and_align.ipynb` | QARTOD + constitution range checks; DOPPIO sigma→z (Vtransform=2); per-time interp to common 2 m × hourly grid. | `outputs/data/raw/*` | `outputs/data/processed/*.parquet` |
| `03_hovmoller_comparison.ipynb` | Figures 1–4: storm track, obs Hovmöller (w/ SBI surface strip), DOPPIO Hovmöller, 4-panel T/S. | processed Parquet | `outputs/figures/001-erin-mab-response/` |
| `04_mixed_layer_response.ipynb` | Potential density via TEOS-10; MLD (both criteria, 25 m ref); sub-window stats; Figures 5–6 + Tables 1–3. | processed Parquet | figures + tables |

### Data sources

- OOI Pioneer MAB South `CP13NOPM-WFP01-03-CTDPFK000` (25–79 m wire-following profiler) and `CP13NOPM-SBI01-02-CTDMOS011` (~0.5 m near-surface CTD) — local kdata mirror.
- Rutgers DOPPIO operational ROMS `2017_da` run, hourly `History_Best` aggregation — OPeNDAP.
- NOAA NHC Tropical Cyclone Report for AL052025 (Erin), final issued 2026-01-30 — Table 1 parsed directly from PDF.

### Testing

```bash
uv run pytest -q    # 15 tests on src/{mld,sigma_to_z,paired_stats}.py
```

### Branch

Implementation lives on `001-erin-mab-response`. PR to `main` when
review complete.

## Notebook format

Notebooks are plain `.ipynb` only — no jupytext paired `.py`. Per
constitution, each notebook is self-contained: it installs its own
pinned dependencies in the first code cell so it can run in Colab
or any fresh Jupyter environment without the project's `uv` venv.

## Layout

- `.specify/memory/constitution.md` — governing standards (PDF at
  `outputs/docs/constitution.pdf`)
- `notebooks/` — exploratory and analysis notebooks
- `outputs/{data,figures,tables,docs}/` — build artifacts
- `literature/{open_access,library_subscription,author_copies,embargoed}/`
  — reference papers (PDFs gitignored; inventory in `literature/README.md`)
- `tests/` — pytest test suite

## Quick start

```bash
uv sync
uv run jupyter lab
```

Regenerate the constitution PDF after any edit to
`.specify/memory/constitution.md`:

```bash
uv run python outputs/docs/make_pdf.py
```
