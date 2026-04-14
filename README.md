# MAB_PioneerV_ROMS

Model–observation comparison between the **OOI Pioneer MAB South
(Coastal Virginia) Array** and regional **ROMS** ocean model output
(DOPPIO / ESPreSSO / NYB-ROMS and successors).

## Status

Spec 001 (`specs/001-erin-mab-response/`): Hurricane Erin (2025) vs.
DOPPIO — constitution, spec, plan, research, and tasks in place.
Implementation in progress on branch `001-erin-mab-response`.

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
