"""Convert methods_spec001.md to methods_spec001.pdf via weasyprint.

Runs from project root:  uv run python outputs/docs/make_methods_pdf.py

The output PDF is gitignored (see .gitignore). Do not commit.
"""
import re
from pathlib import Path

import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
INPUT = HERE / "methods_spec001.md"
OUTPUT = HERE / "methods_spec001.pdf"

md_text = INPUT.read_text()

# Strip YAML front matter if present
if md_text.startswith("---"):
    end = md_text.index("---", 3)
    md_text = md_text[end + 3:].strip()

# Pull the first H1 out to use as the doc title; leave body without it
lines = md_text.splitlines()
doc_title = "Methods — Spec 001"
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
        margin: 0.9in;
        @bottom-center {{
            content: counter(page);
            font-size: 9pt;
            color: #666;
        }}
    }}
    body {{
        font-family: "Courier New", "Courier", monospace;
        font-size: 9.5pt;
        line-height: 1.45;
        color: #222;
    }}
    h1 {{
        font-size: 16pt;
        color: #1a3c6e;
        border-bottom: 2pt solid #1a3c6e;
        padding-bottom: 6pt;
        margin-top: 22pt;
        page-break-before: avoid;
    }}
    h1.doc-title {{
        font-size: 20pt;
        text-align: center;
        border-bottom: none;
        margin-top: 0;
        margin-bottom: 0;
        color: #1a3c6e;
    }}
    h2 {{
        font-size: 12pt;
        color: #2a5a8e;
        margin-top: 16pt;
    }}
    h3 {{
        font-size: 10.5pt;
        color: #2a5a8e;
        margin-top: 12pt;
    }}
    em {{ color: #444; }}
    strong {{ color: #1a1a1a; }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 10pt 0;
        font-size: 9pt;
    }}
    th, td {{
        border: 1px solid #ccc;
        padding: 4pt 8pt;
        text-align: left;
        vertical-align: top;
    }}
    th {{
        background-color: #e8eef5;
        font-weight: bold;
    }}
    tr:nth-child(even) {{ background-color: #f8f9fa; }}
    ul, ol {{ margin: 6pt 0; padding-left: 20pt; }}
    li {{ margin-bottom: 3pt; }}
    code {{
        font-family: "Courier New", "Courier", monospace;
        background-color: #f4f4f4;
        padding: 1pt 3pt;
        border-radius: 2pt;
        font-size: 9pt;
    }}
    pre {{
        background-color: #f4f4f4;
        padding: 6pt;
        border-radius: 3pt;
        font-size: 9pt;
        overflow-x: auto;
    }}
    hr {{
        border: none;
        border-top: 1px solid #bbb;
        margin: 16pt 0;
    }}
    .subtitle {{
        text-align: center;
        font-size: 10pt;
        color: #666;
        margin-top: -6pt;
        margin-bottom: 20pt;
    }}
</style>
</head>
<body>
<h1 class="doc-title">{doc_title}</h1>
<div class="subtitle">Internal review draft — 2026-04-14 — not for distribution</div>
{html_body}
</body>
</html>
"""

HTML(string=html_doc).write_pdf(str(OUTPUT))
print(f"Written to {OUTPUT}")
