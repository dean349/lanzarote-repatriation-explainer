import markdown
import re

INPUT_FILE  = r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_For_Law_Firms.md'
OUTPUT_FILE = r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_For_Law_Firms.html'

print(f"Reading {INPUT_FILE} ...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()

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
    replace_alert,
    raw
)

print("Converting markdown ...")
html_body = markdown.markdown(
    raw,
    extensions=['tables', 'fenced_code', 'toc']
)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Wincham Group Litigation Opportunity — Pitch Report</title>
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
      max-width: 920px;
      margin: 0 auto;
      background: #ffffff;
      padding: 0 0 80px;
      box-shadow: 0 4px 40px rgba(0,0,0,0.10);
      min-height: 100vh;
    }}

    /* ─── Header band ─── */
    .doc-header {{
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      color: #fff;
      padding: 52px 60px 44px;
    }}
    .doc-header .eyebrow {{
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: #94a3b8;
      margin-bottom: 14px;
    }}
    .doc-header h1 {{
      font-size: 2.4em;
      font-weight: 700;
      line-height: 1.2;
      color: #fff;
      margin-bottom: 10px;
    }}
    .doc-header .subtitle {{
      font-size: 1em;
      color: #cbd5e1;
      margin-bottom: 28px;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
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

    /* ─── Confidential ribbon ─── */
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

    /* ─── Body content ─── */
    .content {{
      padding: 48px 60px;
    }}

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
    h3 {{
      font-size: 1em;
      font-weight: 600;
      color: #302b63;
      margin: 28px 0 10px;
    }}
    h4 {{
      font-size: 0.95em;
      font-weight: 600;
      color: #555;
      margin: 20px 0 8px;
    }}

    p {{ margin-bottom: 14px; }}
    ul, ol {{ margin: 10px 0 14px 22px; }}
    li {{ margin-bottom: 6px; }}
    strong {{ color: #0f0c29; }}

    /* ─── Tables ─── */
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

    /* ─── KPI callout boxes ─── */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
    .kpi .kpi-value {{
      font-size: 1.7em;
      font-weight: 700;
      color: #a5b4fc;
      line-height: 1;
    }}
    .kpi .kpi-label {{
      font-size: 11px;
      color: #cbd5e1;
      margin-top: 6px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}

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
      .meta-grid {{ grid-template-columns: repeat(3, 1fr); }}
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
      <div class="eyebrow">Strictly Private &amp; Confidential — Professional Negligence Group Litigation</div>
      <h1>The Wincham Group Litigation Opportunity</h1>
      <div class="subtitle">A Commercial Pitch to UK Professional Negligence Law Firms &amp; Claims Management Companies</div>

      <div class="meta-grid">
        <div class="meta-item">
          <div class="label">Date</div>
          <div class="value">31 March 2026</div>
        </div>
        <div class="meta-item">
          <div class="label">Defendant</div>
          <div class="value">Wincham Accountants Ltd / Adrem Accounting Ltd</div>
        </div>
        <div class="meta-item">
          <div class="label">Victim Pool</div>
          <div class="value">~1,606 identified households</div>
        </div>
        <div class="meta-item">
          <div class="label">TAM (Head 1)</div>
          <div class="value">£25.9 million+</div>
        </div>
        <div class="meta-item">
          <div class="label">TAM (Head 1+2)</div>
          <div class="value">£50–88 million</div>
        </div>
        <div class="meta-item">
          <div class="label">Anchor Claim</div>
          <div class="value">£86,310–£149,807</div>
        </div>
      </div>
    </div>

    <div class="conf-ribbon">⚠ Strictly Private &amp; Confidential — Not For Distribution</div>

    <div class="content">

      <div class="kpi-grid">
        <div class="kpi">
          <div class="kpi-value">1,606</div>
          <div class="kpi-label">Identified victim households</div>
        </div>
        <div class="kpi">
          <div class="kpi-value">589</div>
          <div class="kpi-label">Wincham client companies</div>
        </div>
        <div class="kpi">
          <div class="kpi-value">£50M+</div>
          <div class="kpi-label">Total addressable market</div>
        </div>
        <div class="kpi">
          <div class="kpi-value">Ready</div>
          <div class="kpi-label">Letter of Claim — ready to issue</div>
        </div>
      </div>

      {html_body}

    </div>

    <div class="footer">
      This document was prepared for the exclusive use of the introducing consultant and the law firm or claims management company
      to whom this introduction is made. It does not constitute legal advice. All quantum figures are estimates pending formal
      legal and tax review. Independent verification of all factual assertions is recommended prior to issuance of any formal legal
      document. Contact for this introduction: available exclusively through the presenting consultant.
    </div>

  </div>
</body>
</html>"""

print(f"Writing {OUTPUT_FILE} ...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(HTML)

print("Done.")
