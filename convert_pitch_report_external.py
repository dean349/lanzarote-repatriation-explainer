"""
Regenerates Wincham_Pitch_Report_EXTERNAL.html and .pdf
from the latest .md source (includes §5.6 SIC misclassification finding).
"""
import markdown, re, subprocess, sys, os

WINCHAM_DIR = r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action'
INPUT_FILE  = os.path.join(WINCHAM_DIR, 'Wincham_Pitch_Report_EXTERNAL.md')
HTML_FILE   = os.path.join(WINCHAM_DIR, 'Wincham_Pitch_Report_EXTERNAL.html')
PDF_FILE    = os.path.join(WINCHAM_DIR, 'Wincham_Pitch_Report_EXTERNAL.pdf')

print(f"Reading {INPUT_FILE} ...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()

# ── GitHub-style alert boxes ───────────────────────────────────────────────
ALERT_ICONS = {
    'NOTE':      ('ℹ️',  '#1a73e8', '#e8f0fe', '#174ea6'),
    'TIP':       ('💡',  '#1e8e3e', '#e6f4ea', '#137333'),
    'IMPORTANT': ('❗',  '#e37400', '#fef3e2', '#b45309'),
    'WARNING':   ('⚠️',  '#c77700', '#fef9e7', '#92400e'),
    'CAUTION':   ('🔴',  '#c5221f', '#fce8e6', '#a50e0e'),
}

def replace_alert(m):
    kind  = m.group(1).upper()
    body  = m.group(2).strip().replace('\n> ', '\n')
    icon, border, bg, text = ALERT_ICONS.get(kind, ('📌', '#333', '#f5f5f5', '#333'))
    body_html = markdown.markdown(body)
    return (
        f'<div class="alert alert-{kind.lower()}" style="border-left:4px solid {border};'
        f'background:{bg};padding:14px 18px;margin:20px 0;border-radius:0 6px 6px 0;">'
        f'<div style="color:{border};font-weight:700;margin-bottom:6px;">{icon} {kind}</div>'
        f'<div style="color:{text};font-size:14px;">{body_html}</div></div>'
    )

raw = re.sub(
    r'> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n((?:> .*\n?)*)',
    replace_alert, raw
)

print("Converting markdown ...")
html_body = markdown.markdown(raw, extensions=['tables', 'fenced_code', 'toc'])

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wincham Scheme — External Pitch Report (April 2026)</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
      font-size: 15px;
      line-height: 1.75;
      color: #1e1e2e;
      background: #f0f2f8;
    }}
    .page {{
      max-width: 940px;
      margin: 0 auto;
      background: #fff;
      padding: 0 0 80px;
      box-shadow: 0 4px 40px rgba(0,0,0,0.10);
      min-height: 100vh;
    }}
    .doc-header {{
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      color: #fff;
      padding: 52px 60px 44px;
    }}
    .eyebrow {{
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #94a3b8;
      margin-bottom: 14px;
    }}
    .doc-header h1 {{
      font-size: 2.3em;
      font-weight: 700;
      line-height: 1.2;
      color: #fff;
      margin-bottom: 10px;
    }}
    .subtitle {{
      font-size: 1em;
      color: #cbd5e1;
      margin-bottom: 28px;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
      gap: 10px;
      margin-top: 28px;
    }}
    .meta-item {{
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 8px;
      padding: 10px 14px;
    }}
    .meta-item .label {{
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 1.5px;
      color: #94a3b8;
      text-transform: uppercase;
    }}
    .meta-item .value {{
      font-size: 13px;
      color: #e2e8f0;
      margin-top: 2px;
    }}
    .conf-ribbon {{
      background: #c5221f;
      color: #fff;
      text-align: center;
      padding: 10px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 2.5px;
      text-transform: uppercase;
    }}
    .updated-banner {{
      background: #1a5c2a;
      color: #fff;
      text-align: center;
      padding: 8px;
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: 1px;
    }}
    .content {{ padding: 48px 60px; }}
    h2 {{
      font-size: 1.15em;
      font-weight: 700;
      color: #0f0c29;
      margin: 44px 0 12px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e8eaf6;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    h3 {{ font-size: 1em; font-weight: 600; color: #302b63; margin: 28px 0 10px; }}
    h4 {{ font-size: 0.95em; font-weight: 600; color: #555; margin: 20px 0 8px; }}
    p {{ margin-bottom: 14px; }}
    ul, ol {{ margin: 10px 0 14px 22px; }}
    li {{ margin-bottom: 6px; }}
    strong {{ color: #0f0c29; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0 28px;
      font-size: 13.5px;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    }}
    thead th {{
      background: #302b63;
      color: #fff;
      padding: 11px 16px;
      text-align: left;
      font-weight: 600;
      font-size: 12.5px;
    }}
    tbody td {{
      padding: 10px 16px;
      border-bottom: 1px solid #eef0f8;
      vertical-align: top;
    }}
    tbody tr:nth-child(even) {{ background: #f8f9ff; }}
    tbody tr:last-child td {{ border-bottom: none; }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 16px;
      margin: 24px 0 32px;
    }}
    .kpi {{
      background: linear-gradient(135deg, #302b63, #24243e);
      color: #fff;
      border-radius: 10px;
      padding: 20px 18px;
      text-align: center;
    }}
    .kpi .kpi-value {{ font-size: 1.7em; font-weight: 700; color: #a5b4fc; line-height: 1; }}
    .kpi .kpi-label {{ font-size: 11px; color: #cbd5e1; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; }}
    blockquote {{
      border-left: 4px solid #302b63;
      background: #f0f2f8;
      padding: 14px 18px;
      margin: 18px 0;
      border-radius: 0 6px 6px 0;
      color: #302b63;
      font-style: italic;
      font-size: 14px;
    }}
    hr {{ border: none; border-top: 1px solid #eef0f8; margin: 36px 0; }}
    .footer {{
      margin: 0 60px;
      padding-top: 20px;
      border-top: 1px solid #eef0f8;
      font-size: 11.5px;
      color: #94a3b8;
      line-height: 1.6;
    }}
    @media print {{
      body {{ background: white; }}
      .page {{ box-shadow: none; }}
    }}
    @media (max-width: 700px) {{
      .doc-header {{ padding: 32px 20px 28px; }}
      .doc-header h1 {{ font-size: 1.5em; }}
      .content {{ padding: 28px 20px; }}
      .footer {{ margin: 0 20px; }}
    }}
  </style>
</head>
<body>
  <div class="page">

    <div class="doc-header">
      <div class="eyebrow">Strictly Private &amp; Confidential — Group Litigation Opportunity</div>
      <h1>The Wincham Scheme — External Pitch Report</h1>
      <div class="subtitle">Prepared for UK Claims Management Companies &amp; Professional Negligence Law Firms</div>
      <div class="meta-grid">
        <div class="meta-item"><div class="label">Updated</div><div class="value">April 2026</div></div>
        <div class="meta-item"><div class="label">Defendants</div><div class="value">Wincham Accountants / Adrem Accounting</div></div>
        <div class="meta-item"><div class="label">Victim Pool</div><div class="value">782 companies / ~1,564 households</div></div>
        <div class="meta-item"><div class="label">TAM (Head 1)</div><div class="value">£25.9 million+</div></div>
        <div class="meta-item"><div class="label">TAM (Total)</div><div class="value">£50–88 million</div></div>
        <div class="meta-item"><div class="label">SIC Mis-filed</div><div class="value">167 companies (85% of Adrem cohort)</div></div>
      </div>
    </div>

    <div class="conf-ribbon">⚠ Strictly Private &amp; Confidential — Not For Distribution</div>
    <div class="updated-banner">✅ Updated April 2026 — Includes §5.6 SIC Code Misclassification Finding &amp; Verified Victim Database (801 clean records)</div>

    <div class="content">

      <div class="kpi-grid">
        <div class="kpi"><div class="kpi-value">782</div><div class="kpi-label">Client companies identified</div></div>
        <div class="kpi"><div class="kpi-value">~1,564</div><div class="kpi-label">Victim households</div></div>
        <div class="kpi"><div class="kpi-value">£50M+</div><div class="kpi-label">Total addressable market</div></div>
        <div class="kpi"><div class="kpi-value">85%</div><div class="kpi-label">SIC misclassification rate</div></div>
        <div class="kpi"><div class="kpi-value">801</div><div class="kpi-label">Verified clean contacts</div></div>
        <div class="kpi"><div class="kpi-value">Ready</div><div class="kpi-label">Database &amp; letter of claim</div></div>
      </div>

      {html_body}

    </div>

    <div class="footer">
      This document was prepared for the exclusive use of the introducing consultant and the law firm or claims management
      company to whom this introduction is made. It does not constitute legal advice. All quantum figures are estimates
      pending formal legal and tax review. Independent verification of all factual assertions is recommended prior to
      issuance of any formal legal document. Victim database v2 (April 2026): 801 verified contacts, operator-filtered.
      Contact for this introduction: available exclusively through the presenting consultant.
    </div>

  </div>
</body>
</html>"""

print(f"Writing HTML → {HTML_FILE}")
with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(HTML)
print("  ✓ HTML written")

# ── PDF via weasyprint or playwright ──────────────────────────────────────
print("Generating PDF ...")
try:
    from weasyprint import HTML as WP_HTML
    WP_HTML(filename=HTML_FILE).write_pdf(PDF_FILE)
    print(f"  ✓ PDF (weasyprint) → {PDF_FILE}")
except ImportError:
    # Fallback: use playwright chromium
    try:
        result = subprocess.run([
            sys.executable, '-m', 'playwright', 'pdf',
            HTML_FILE, PDF_FILE
        ], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"  ✓ PDF (playwright) → {PDF_FILE}")
        else:
            # Second fallback: use the existing convert_html_to_pdf.py approach
            script = r'C:\DAD\UK_Lanzarote_Repatriation\convert_html_to_pdf.py'
            if os.path.exists(script):
                subprocess.run([sys.executable, script, HTML_FILE, PDF_FILE], timeout=120)
                print(f"  ✓ PDF (convert_html_to_pdf) → {PDF_FILE}")
            else:
                print("  ⚠ PDF generation skipped — install weasyprint: pip install weasyprint")
    except Exception as e:
        print(f"  ⚠ PDF fallback failed: {e}")
        print("  Run manually: python convert_html_to_pdf.py")

print("\n✅ Both files updated with §5.6 SIC misclassification and April 2026 victim database stats.")
