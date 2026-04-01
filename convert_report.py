import markdown
import re
import sys

INPUT_FILE  = r'c:/DAD/UK_Lanzarote_Repatriation/divorce_financial_report_v2.md'
OUTPUT_FILE = r'c:/DAD/UK_Lanzarote_Repatriation/divorce_financial_report.html'

print(f"Reading {INPUT_FILE} ...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()

# Convert GitHub-style alerts (> [!NOTE], > [!IMPORTANT] etc.) to styled divs
ALERT_ICONS = {
    'NOTE':      ('ℹ️',  '#1a73e8', '#e8f0fe'),
    'TIP':       ('💡',  '#1e8e3e', '#e6f4ea'),
    'IMPORTANT': ('❗',  '#e37400', '#fef3e2'),
    'WARNING':   ('⚠️',  '#f29900', '#fef3e2'),
    'CAUTION':   ('🔴',  '#d93025', '#fce8e6'),
}

def replace_alert(m):
    kind  = m.group(1).upper()
    body  = m.group(2).strip().replace('\n> ', '\n')
    icon, color, bg = ALERT_ICONS.get(kind, ('📌', '#333', '#f5f5f5'))
    return (
        f'<div class="alert" style="border-left:4px solid {color};'
        f'background:{bg};padding:12px 16px;margin:16px 0;border-radius:4px;">'
        f'<strong style="color:{color}">{icon} {kind}</strong><br>'
        f'{body}</div>'
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
  <title>Confidential Financial &amp; Divorce Settlement Report</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      font-size: 15px;
      line-height: 1.7;
      color: #2c2c2c;
      background: #f7f8fc;
      padding: 0;
    }}
    .page {{
      max-width: 860px;
      margin: 0 auto;
      background: #fff;
      padding: 48px 56px 64px;
      box-shadow: 0 2px 24px rgba(0,0,0,0.08);
      min-height: 100vh;
    }}
    .confidential-banner {{
      background: #d93025;
      color: #fff;
      text-align: center;
      padding: 10px;
      font-weight: 700;
      font-size: 13px;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin: -48px -56px 40px;
    }}
    h1 {{ font-size: 1.9em; color: #1a1a2e; margin-bottom: 6px; line-height: 1.25; }}
    h2 {{ font-size: 1.25em; color: #1a73e8; margin: 36px 0 12px; border-bottom: 2px solid #e8f0fe; padding-bottom: 6px; }}
    h3 {{ font-size: 1.05em; color: #2c2c2c; margin: 24px 0 8px; }}
    p {{ margin-bottom: 12px; }}
    ul, ol {{ margin: 10px 0 14px 24px; }}
    li {{ margin-bottom: 6px; }}
    strong {{ color: #1a1a2e; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 14px;
    }}
    th {{
      background: #1a73e8;
      color: #fff;
      padding: 10px 14px;
      text-align: left;
    }}
    td {{ padding: 9px 14px; border-bottom: 1px solid #e0e0e0; }}
    tr:nth-child(even) {{ background: #f8f9ff; }}
    blockquote {{
      border-left: 4px solid #1a73e8;
      background: #e8f0fe;
      padding: 12px 16px;
      margin: 16px 0;
      border-radius: 0 4px 4px 0;
      color: #0d47a1;
      font-style: italic;
    }}
    .alert {{ font-size: 14px; }}
    hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 32px 0; }}
    .footer {{
      margin-top: 48px;
      font-size: 12px;
      color: #888;
      border-top: 1px solid #eee;
      padding-top: 16px;
    }}
    @media print {{
      body {{ background: white; }}
      .page {{ box-shadow: none; padding: 20px; }}
      .confidential-banner {{ margin: -20px -20px 32px; }}
    }}
    @media (max-width: 700px) {{
      .page {{ padding: 24px 18px 40px; }}
      .confidential-banner {{ margin: -24px -18px 28px; font-size: 11px; }}
      h1 {{ font-size: 1.4em; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="confidential-banner">⚠ Strictly Private &amp; Confidential — Not for Distribution</div>
    {html_body}
    <div class="footer">
      This report synthesises existing workspace data with UK family law principles.
      It is for strategic planning purposes only and does not constitute formal legal advice.
      Philip Harrison must engage a qualified UK family law solicitor before taking any action.
    </div>
  </div>
</body>
</html>"""

print(f"Writing {OUTPUT_FILE} ...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(HTML)

print("Done. File written successfully.")
