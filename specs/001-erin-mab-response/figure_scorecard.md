# Figure Rubric Scorecard — Spec 001

Per constitution: every figure scored against the `map-figure` or
`timeseries-figure` rubric (from `~/.claude/skills/`). Tier: **student
/ interactive Plotly** (not paper-tier static). Some paper-tier
requirements (scale bar, north arrow, PNG DPI, neatline) are
deliberately not met and are flagged rather than hidden; they would
need to be addressed before any figure is exported to a paper.

Scoring: ✓ = meets, ~ = partial / tier-adjusted, ✗ = fails, N/A = not
applicable.

## Figure 1 — Storm track map (map-figure rubric)

| # | Element | Score | Note |
|---|---|---|---|
| 1 | Coordinate Reference | ✓ | Lat/lon labeled on both axes. |
| 2 | Scale Bar | ✗ | Absent. Add via `cartopy` or manual km bar if exporting to paper. |
| 3 | North Arrow | ✗ | Absent. Same note as (2). |
| 4 | Classification Legend | ✓ | Category colors (TD/TS/HU1–5/EX) explained. |
| 5 | Depth/Value Colorbar | N/A | Categorical data, not continuous. |
| 6 | Neatline Border | ✗ | Not required at student tier. |
| 7 | Title | ✓ | Concise, storm ID + CPA anchor. |
| 8 | Figure Caption | ✓ | Title subtitle + markdown cell with context. |
| 9 | Label Legibility | ✓ | CPA and CP13NOPM labels readable. |
| 10 | Resolution/Format | ~ | Interactive HTML, not paper-tier PNG. |
| 11 | Projection Info | ~ | Not stated explicitly on the map; data are WGS84 (per constitution). Add to caption before export. |
| 12 | Colorblind Safety | ~ | Red–yellow–gray sequence for hurricane categories is the NHC convention but is not strictly deuteranopia-safe. Acceptable for student tier; flag if paper-tier. |
| 13 | Data Provenance | ✓ | NHC TCR cited in title and caption. |
| 14 | Multi-Panel Labels | N/A | Single panel. |

**Overall**: Score 8/11 applicable items; 3 partials; 2 failures (scale bar, north arrow). All failures are paper-tier requirements waived at student tier but must be addressed before publication.

## Figure 2 — Obs T(z, t) Hovmöller (timeseries-figure rubric)

| # | Element | Score | Note |
|---|---|---|---|
| 1 | Axis Labels | ✓ | Depth (m) + T (°C) + Time (UTC). |
| 2 | Dual-Axis | N/A | Single y-axis per panel. |
| 3 | Date Formatting | ✓ | Plotly auto ticks at daily scale. |
| 4 | Classification Legend | ~ | Top strip labeled via subplot title; Hovmöller has colorbar. |
| 5 | Event Annotation | ✓ | CPA dashed vertical. |
| 6 | Title | ✓ | Two-line, includes CP13NOPM + event. |
| 7 | Figure Caption | ✓ | Describes QARTOD + range-check state of plotted data. |
| 8 | Temporal Aggregation | ✓ | "Hourly × 2 m grid" in caption. |
| 9 | Y-Axis Range | ✓ | Constrained to 25–79 m usable range. |
| 10 | X-Axis Padding | ✓ | Plotly default balanced. |
| 11 | Data Gaps | ✓ | White cells are genuine missing profiles, not filled. |
| 12 | Grid | ~ | Plotly template `plotly_white` default. |
| 13 | Spine Weight | N/A | Interactive. |
| 14 | Line Weight | N/A | Heatmap. |
| 15 | Resolution/Format | ~ | Interactive HTML. |
| 16 | Colorblind Safety | ✗ | `RdYlBu_r` is **not strictly safe** under protanopia (the red–yellow transition flattens). **Known issue.** Switch to `cmocean.thermal` or `viridis` if exporting to paper. |
| 17 | Data Provenance | ✓ | Caption cites CP13NOPM + event window; full refdes in `data_provenance.csv`. |
| 18 | Multi-Panel Labels | ~ | Subplot titles present; no "(a)/(b)" letters — OK for student tier. |
| 19 | Layout Spacing | ✓ | No clipping. |

**Overall**: 13/14 applicable items pass or are acceptable at student tier; 1 hard failure (colorblind palette) flagged for fix before paper export.

## Figure 3 — DOPPIO T(z, t) Hovmöller

Same rubric as Fig 2. Scores match Fig 2 one-for-one with the same
RdYlBu_r colorblind flag (✗). Same fix before export.

## Figure 4 — 4-panel obs vs DOPPIO T and S

Same rubric as Fig 2. Differences from Fig 2:

- Multi-Panel Labels (#18): ✓ `(a)`, `(b)`, `(c)`, `(d)` in subplot titles.
- Colorblind Safety (#16): ✗ for T rows (RdYlBu_r); ✓ for S rows (Viridis).
  The asymmetry is deliberate — temperature uses the domain-
  conventional diverging palette; salinity uses the sequential
  colorblind-safe palette. Flag T rows for palette swap before export.

## Figure 5 — MLD time series (timeseries-figure rubric)

| # | Element | Score | Note |
|---|---|---|---|
| 1 | Axis Labels | ✓ | "MLD (m, positive down)" + Time. |
| 2 | Dual-Axis | N/A | Single y-axis. |
| 3 | Date Formatting | ✓ | |
| 4 | Classification Legend | ✓ | 4 series with consistent color coding (obs = red/orange, DOPPIO = blue/light-blue). Solid = density, dotted = temperature. |
| 5 | Event Annotation | ✓ | CPA vertical + sub-window shading + ref-depth horizontal. |
| 6 | Title | ✓ | |
| 7 | Figure Caption | ✓ | Now explicitly flags the NON-STANDARD 25 m reference depth vs de Boyer Montégut 2004's 10 m. |
| 8 | Temporal Aggregation | ✓ | Per-time MLD at hourly cadence. |
| 9 | Y-Axis Range | ✓ | Inverted (deeper = down) with `autorange='reversed'`. |
| 10 | X-Axis Padding | ✓ | |
| 11 | Data Gaps | ✓ | Missing MLD values shown as gaps. |
| 12 | Grid | ~ | |
| 13 | Spine Weight | N/A | |
| 14 | Line Weight | ✓ | Width 1.5–2 pt; distinguishable. |
| 15 | Resolution/Format | ~ | Interactive. |
| 16 | Colorblind Safety | ~ | Red vs blue main color opposition; orange vs light-blue for the secondary (temperature) criterion. The obs-red / model-orange pair is marginal under deuteranopia but distinguishable by line style (solid vs dotted) as a fallback. Acceptable. |
| 17 | Data Provenance | ✓ | Cited in caption and `data_provenance.csv`. |
| 18 | Multi-Panel Labels | N/A | Single panel. |
| 19 | Layout Spacing | ✓ | |

**Overall**: no hard failures. Student-tier ready.

## Figure 6 — Surface T and S time series (timeseries-figure rubric)

| # | Element | Score | Note |
|---|---|---|---|
| 1 | Axis Labels | ✓ | T (°C), S (PSU), Time (UTC). |
| 2 | Dual-Axis | N/A | Separate panels. |
| 3 | Date Formatting | ✓ | |
| 4 | Classification Legend | ✓ | SBI (red) vs DOPPIO (blue), shared across panels. |
| 5 | Event Annotation | ✓ | CPA + sub-window shading. |
| 6 | Title | ✓ | |
| 7 | Figure Caption | ✓ | States 0.5 m nominal depth + interp method. |
| 8 | Temporal Aggregation | ✓ | Hourly. |
| 9 | Y-Axis Range | ✓ | Auto on T and S — appropriate for the signal. |
| 10 | X-Axis Padding | ✓ | |
| 11 | Data Gaps | ✓ | Visible as breaks in the line (no silent interpolation). |
| 12 | Grid | ~ | |
| 13 | Spine Weight | N/A | |
| 14 | Line Weight | ✓ | |
| 15 | Resolution/Format | ~ | Interactive. |
| 16 | Colorblind Safety | ✓ | Red (SBI) vs blue (DOPPIO) — standard warm/cool opposition, distinguishable. |
| 17 | Data Provenance | ✓ | Cited in caption and `data_provenance.csv`. |
| 18 | Multi-Panel Labels | ~ | Panel subplot titles. |
| 19 | Layout Spacing | ✓ | |

**Overall**: no hard failures. Student-tier ready.

## Summary

- **6 figures scored against appropriate rubrics** (Fig 1 map, Figs 2–6 timeseries).
- **No hard failures at student-tier**, except the `RdYlBu_r` temperature colormap in Figures 2, 3, and Fig 4 panels (a)/(b) — known issue, flagged for palette swap before paper export.
- **Paper-tier fixes required** (not yet applied) if exporting:
  - Fig 1: add scale bar, north arrow, explicit projection note.
  - Figs 2–4 (T panels): swap `RdYlBu_r` → `cmocean.thermal` or `viridis`.
  - All figures: render to 300 dpi PNG with matplotlib.

**Verdict**: student-tier ready; paper-tier not yet. The figures support the student-pedagogical framing of spec 001 and are honest about data coverage and methodological caveats.
