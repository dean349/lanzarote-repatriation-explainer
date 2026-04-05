r"""
generate_all_pdfs_playwright.py
Converts all Wincham case markdown documents to professionally styled PDFs
using Playwright (headless Chromium) — no GTK/Pango/wkhtmltopdf dependencies.
Run from: c:\DAD\UK_Lanzarote_Repatriation
"""

import re
import sys
from pathlib import Path
import markdown

PDF_DIR = Path(r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham Scheme-Legal Claims-Victims')

DOCS = [
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_For_Law_Firms.md',
        'output': PDF_DIR / 'Wincham_Pitch_Report_For_Law_Firms.pdf',
        'title': 'The Wincham Group Litigation Opportunity — Internal Pitch Report',
        'subtitle': 'A Commercial Pitch to UK Professional Negligence Law Firms',
        'eyebrow': 'STRICTLY PRIVATE & CONFIDENTIAL',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_EXTERNAL.md',
        'output': PDF_DIR / 'Wincham_Pitch_Report_EXTERNAL.pdf',
        'title': 'The Wincham Group Litigation Opportunity',
        'subtitle': 'External Commercial Pitch — Law Firm & CMC Edition',
        'eyebrow': 'STRICTLY PRIVATE & CONFIDENTIAL — NOT FOR DISTRIBUTION',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Ellis_Briefing_Document.md',
        'output': PDF_DIR / 'Ellis_Briefing_Document.pdf',
        'title': 'Ellis Harrison — Full Operational Briefing',
        'subtitle': 'Project: Wincham Group Litigation Data Programme',
        'eyebrow': 'PRIVATE & CONFIDENTIAL — FOR ADDRESSEE ONLY',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Legal_Lead_Generation_Business_Plan.md',
        'output': PDF_DIR / 'Wincham_Legal_Lead_Generation_Business_Plan.pdf',
        'title': 'The Wincham Litigation Lead Generation Playbook',
        'subtitle': 'Executive Strategy & Business Operations Report',
        'eyebrow': 'CONFIDENTIAL OPERATIONS REPORT',
        'ribbon': False,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Public_Evidence_Dossier.md',
        'output': PDF_DIR / 'Wincham_Public_Evidence_Dossier.pdf',
        'title': 'Wincham Group — Public Evidence Dossier',
        'subtitle': 'Forensic Evidence Compilation for Professional Negligence Proceedings',
        'eyebrow': 'PRIVILEGED & CONFIDENTIAL — LITIGATION SUPPORT',
        'ribbon': True,
    },
]

ALERT_ICONS = {
    'NOTE':      ('ℹ️',  '#1a73e8', '#e8f0fe', '#174ea6'),
    'TIP':       ('💡',  '#1e8e3e', '#e6f4ea', '#137333'),
    'IMPORTANT': ('❗',  '#e37400', '#fef3e2', '#b45309'),
    'WARNING':   ('⚠️',  '#c77700', '#fef9e7', '#92400e'),
    'CAUTION':   ('🔴',  '#c5221f', '#fce8e6', '#a50e0e'),
}

def replace_alert(m):
    kind = m.group(1).upper()
    body = m.group(2).strip().replace('\n> ', '\n')
    icon, border, bg, text_colour = ALERT_ICONS.get(kind, ('📌', '#333', '#f5f5f5', '#333'))
    body_html = markdown.markdown(body)
    return (
        f'<div style="border-left:4px solid {border};background:{bg};'
        f'padding:14px 18px;margin:20px 0;border-radius:0 6px 6px 0;">'
        f'<div style="color:{border};font-weight:700;margin-bottom:6px;">{icon} {kind}</div>'
        f'<div style="color:{text_colour};font-size:14px;">{body_html}</div></div>'
    )

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.75;
  color: #1e1e2e;
  background: #fff;
}
.doc-header {
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  color: #fff;
  padding: 48px 56px 40px;
}
.eyebrow {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: #94a3b8;
  margin-bottom: 12px;
}
.doc-header h1 { font-size: 2em; font-weight: 700; color: #fff; margin-bottom: 8px; line-height: 1.2; }
.subtitle { font-size: 0.95em; color: #cbd5e1; }
.conf-ribbon {
  background: #c5221f;
  color: #fff;
  text-align: center;
  padding: 9px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2.5px;
  text-transform: uppercase;
}
.content { padding: 40px 56px 60px; }
h2 {
  font-size: 1.05em;
  font-weight: 700;
  color: #0f0c29;
  margin: 40px 0 10px;
  padding-bottom: 7px;
  border-bottom: 2px solid #e8eaf6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
h3 { font-size: 0.97em; font-weight: 600; color: #302b63; margin: 24px 0 8px; }
h4 { font-size: 0.93em; font-weight: 600; color: #555; margin: 18px 0 6px; }
p { margin-bottom: 12px; }
ul, ol { margin: 8px 0 12px 22px; }
li { margin-bottom: 5px; }
strong { color: #0f0c29; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 18px 0 24px;
  font-size: 12.5px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
thead th {
  background: #302b63;
  color: #fff;
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  font-size: 11.5px;
}
tbody td {
  padding: 9px 14px;
  border-bottom: 1px solid #eef0f8;
  vertical-align: top;
}
tbody tr:nth-child(even) { background: #f8f9ff; }
tbody tr:last-child td { border-bottom: none; }
blockquote {
  border-left: 4px solid #302b63;
  background: #f0f2f8;
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 6px 6px 0;
  color: #302b63;
  font-style: italic;
  font-size: 13px;
}
hr { border: none; border-top: 1px solid #eef0f8; margin: 32px 0; }
.footer {
  margin: 0 56px;
  padding-top: 18px;
  border-top: 1px solid #eef0f8;
  font-size: 10.5px;
  color: #94a3b8;
  line-height: 1.6;
}
a { color: #302b63; }
@page { size: A4; margin: 0; }
"""

def build_html(doc, body_html):
    ribbon = (
        '<div class="conf-ribbon">'
        '&#9888; STRICTLY PRIVATE &amp; CONFIDENTIAL — NOT FOR DISTRIBUTION'
        '</div>'
    ) if doc['ribbon'] else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{doc['title']}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="doc-header">
    <div class="eyebrow">{doc['eyebrow']}</div>
    <h1>{doc['title']}</h1>
    <p class="subtitle">{doc['subtitle']}</p>
  </div>
  {ribbon}
  <div class="content">
    {body_html}
  </div>
  <div class="footer">
    This document was prepared for professional use only. It does not constitute legal advice.
    All quantum figures are estimates pending formal legal and tax review.
    Contact exclusively through the presenting consultant. Updated: April 2026.
  </div>
</body>
</html>"""

def md_to_html(md_text):
    md_text = re.sub(
        r'> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n((?:> .*\n?)*)',
        replace_alert,
        md_text
    )
    return markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

# ── Main ──────────────────────────────────────────────────────────────────────

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && python -m playwright install chromium")
    sys.exit(1)

tmp_html = Path(r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_pdf_render.html')

print(f"\nGenerating {len(DOCS)} PDFs using Playwright (headless Chromium)...\n")

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()

    for doc in DOCS:
        inpath = Path(doc['input'])
        outpath = Path(doc['output'])
        print(f"  ⏳  {inpath.name}")

        raw = inpath.read_text(encoding='utf-8')
        body_html = md_to_html(raw)
        html_content = build_html(doc, body_html)

        tmp_html.write_text(html_content, encoding='utf-8')
        page.goto(tmp_html.as_uri(), wait_until='networkidle', timeout=30000)
        page.pdf(
            path=str(outpath),
            format='A4',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'},
        )
        print(f"  ✅  {outpath.name}  ({outpath.stat().st_size // 1024} KB)")

    browser.close()

tmp_html.unlink(missing_ok=True)
print("\n✅ All PDFs generated successfully.")
