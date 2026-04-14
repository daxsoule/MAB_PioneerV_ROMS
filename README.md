# MAB_PioneerV_ROMS

Model–observation comparison between the **OOI Pioneer MAB South
(Coastal Virginia) Array** and regional **ROMS** ocean model output
(DOPPIO / ESPreSSO / NYB-ROMS and successors).

## Status

New project — scaffold only. Scientific spec pending (`/speckit.specify`).

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
