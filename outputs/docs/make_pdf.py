"""Convert the project constitution markdown to PDF via weasyprint.

Reads `.specify/memory/constitution.md` from the project root and writes
`outputs/docs/constitution.pdf`. Run from the project root with
`uv run python outputs/docs/make_pdf.py`, or from this directory with
`uv run python make_pdf.py`.
"""
import re
from pathlib import Path

import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
INPUT = PROJECT_ROOT / ".specify" / "memory" / "constitution.md"
OUTPUT = HERE / "constitution.pdf"

md_text = INPUT.read_text()

if md_text.startswith("---"):
    end = md_text.index("---", 3)
    md_text = md_text[end + 3:].strip()

md_text = re.sub(
    r'\\review\{([^}]+)\}',
    r'<div class="review">&#9998; Review needed: \1</div>',
    md_text,
)
md_text = md_text.replace(r'$\geq$', '≥')

# Strip the first H1 — it becomes the styled doc title below.
lines = md_text.splitlines()
doc_title = "Pioneer NES Mid-Atlantic Bight CTD Analysis Research Constitution"
for i, line in enumerate(lines):
    if line.startswith("# "):
        doc_title = line[2:].strip()
        lines.pop(i)
        break
md_text = "\n".join(lines).lstrip()

html_body = markdown.markdown(md_text, extensions=["tables", "smarty"])

html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: letter;
        margin: 1in;
        @bottom-center {{
            content: counter(page);
            font-size: 9pt;
            color: #666;
        }}
    }}
    body {{
        font-family: "Courier New", "Courier", monospace;
        font-size: 10pt;
        line-height: 1.5;
        color: #222;
    }}
    h1 {{
        font-size: 18pt;
        color: #1a3c6e;
        border-bottom: 2pt solid #1a3c6e;
        padding-bottom: 6pt;
        margin-top: 24pt;
    }}
    h1.doc-title {{
        font-size: 22pt;
        text-align: center;
        border-bottom: none;
        margin-top: 0;
        margin-bottom: 0;
        color: #1a3c6e;
    }}
    h2 {{
        font-size: 13pt;
        color: #2a5a8e;
        margin-top: 18pt;
    }}
    h3 {{
        font-size: 11pt;
        color: #2a5a8e;
        margin-top: 12pt;
    }}
    strong {{ color: #1a1a1a; }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 12pt 0;
    }}
    th, td {{
        border: 1px solid #ccc;
        padding: 6pt 10pt;
        text-align: left;
    }}
    th {{
        background-color: #e8eef5;
        font-weight: bold;
    }}
    tr:nth-child(even) {{ background-color: #f8f9fa; }}
    ul, ol {{ margin: 6pt 0; }}
    li {{ margin-bottom: 4pt; }}
    code {{
        font-family: "Courier New", "Courier", monospace;
        background-color: #f4f4f4;
        padding: 1pt 3pt;
        border-radius: 2pt;
    }}
    .review {{
        background-color: #fff3f3;
        border-left: 4pt solid #c44;
        padding: 8pt 12pt;
        margin: 10pt 0;
        color: #922;
        font-style: italic;
    }}
    .subtitle {{
        text-align: center;
        font-size: 11pt;
        color: #666;
        margin-top: -8pt;
        margin-bottom: 24pt;
    }}
</style>
</head>
<body>
<h1 class="doc-title">{doc_title}</h1>
<div class="subtitle">Draft — 2026-04-14</div>
{html_body}
</body>
</html>
"""

HTML(string=html_doc).write_pdf(str(OUTPUT))
print(f"Written to {OUTPUT}")
