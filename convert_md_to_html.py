#!/usr/bin/env python3
"""
convert_md_to_html.py
Converts missing Wincham .md files to styled HTML matching the established template.
"""

import re
import sys
import subprocess

# ---------------------------------------------------------------------------
# Try to import markdown; install if missing
# ---------------------------------------------------------------------------
try:
    import markdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"], stdout=subprocess.DEVNULL)
    import markdown

BASE_DIR = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"

# ---------------------------------------------------------------------------
# Shared CSS / header template
# ---------------------------------------------------------------------------
HTML_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap');
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'EB Garamond',Georgia,serif;font-size:16px;line-height:1.8;color:#1a1a1a;background:#f5f0e8}
    .page{max-width:860px;margin:0 auto;background:#fff;padding:0 0 80px;box-shadow:0 4px 40px rgba(0,0,0,.15);min-height:100vh}
    .doc-header{background:#1a1a2e;color:#fff;padding:52px 60px 44px}
    .doc-header .eyebrow{font-family:'Inter',sans-serif;font-size:10px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#94a3b8;margin-bottom:14px}
    .doc-header h1{font-size:1.9em;font-weight:600;line-height:1.25;color:#fff;margin-bottom:8px}
    .doc-header .subtitle{font-size:0.9em;font-family:'Inter',sans-serif;color:#cbd5e1}
    .conf-ribbon{background:#8b0000;color:#fff;text-align:center;padding:10px;font-family:'Inter',sans-serif;font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase}
    .content{padding:52px 60px}
    h1{display:none}
    h2{font-size:1em;font-weight:600;font-family:'Inter',sans-serif;color:#1a1a2e;margin:44px 0 12px;padding-bottom:8px;border-bottom:2px solid #e8e0d0;text-transform:uppercase;letter-spacing:1px}
    h3{font-size:1em;font-weight:600;font-family:'Inter',sans-serif;color:#555;margin:28px 0 10px}
    h4{font-size:.9em;font-weight:600;font-family:'Inter',sans-serif;color:#777;margin:20px 0 8px}
    p{margin-bottom:14px}
    ul,ol{margin:10px 0 14px 24px}
    li{margin-bottom:6px}
    strong{color:#1a1a2e}
    table{width:100%;border-collapse:collapse;margin:20px 0 28px;font-size:14px;font-family:'Inter',sans-serif}
    thead th{background:#1a1a2e;color:#fff;padding:10px 16px;text-align:left;font-weight:600;font-size:12px}
    tbody td{padding:10px 16px;border-bottom:1px solid #eee;vertical-align:top}
    tbody tr:nth-child(even){background:#faf8f4}
    tbody tr:last-child td{border-bottom:none}
    blockquote{border-left:4px solid #1a1a2e;background:#f5f0e8;padding:14px 18px;margin:18px 0;border-radius:0 4px 4px 0;font-style:italic;font-size:15px;color:#333}
    hr{border:none;border-top:1px solid #e8e0d0;margin:36px 0}
    code{background:#f5f0e8;padding:2px 6px;border-radius:3px;font-size:13px;font-family:monospace}
    pre{background:#1a1a2e;color:#e2e8f0;padding:18px;border-radius:6px;overflow-x:auto;font-size:13px;margin:18px 0}
    pre code{background:none;padding:0;color:inherit}
    .callout{border-radius:0 6px 6px 0;padding:14px 18px;margin:20px 0}
    .callout-note{border-left:4px solid #1e40af;background:#dbeafe}
    .callout-note .callout-title{color:#1e40af}
    .callout-tip{border-left:4px solid #166534;background:#dcfce7}
    .callout-tip .callout-title{color:#166534}
    .callout-important{border-left:4px solid #7e22ce;background:#f3e8ff}
    .callout-important .callout-title{color:#7e22ce}
    .callout-warning{border-left:4px solid #92400e;background:#fef3c7}
    .callout-warning .callout-title{color:#92400e}
    .callout-caution{border-left:4px solid #991b1b;background:#fee2e2}
    .callout-caution .callout-title{color:#991b1b}
    .callout-title{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px}
    .callout-body{font-style:normal;font-size:15px}
    .footer{margin:0 60px;padding-top:20px;border-top:1px solid #e8e0d0;font-family:'Inter',sans-serif;font-size:11px;color:#999;line-height:1.6}
    @media(max-width:700px){.doc-header,.content{padding:28px 20px}.footer{margin:0 20px}}
    @media print{body{background:#fff}.page{box-shadow:none}}
"""

CALLOUT_ICONS = {
    'NOTE': '📋',
    'TIP': '💡',
    'IMPORTANT': '⚠️',
    'WARNING': '⚠️',
    'CAUTION': '🔴',
}


# ---------------------------------------------------------------------------
# Pre-processor: GitHub-style callouts → sentinel divs
# ---------------------------------------------------------------------------
def preprocess_callouts(text):
    """
    Replace GitHub-style callout blocks:
        > [!TYPE]
        > content lines
    with <div class="callout callout-type">...</div> markers that survive
    the markdown pipeline.
    """
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        m = re.match(r'^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$', line.rstrip())
        if m:
            ctype = m.group(1)
            icon = CALLOUT_ICONS.get(ctype, '📌')
            # Collect continuation > lines
            body_lines = []
            i += 1
            while i < len(lines) and lines[i].startswith('>'):
                body_lines.append(lines[i][1:].lstrip())
                i += 1
            body_md = '\n'.join(body_lines)
            # Convert the body markdown separately
            body_html = markdown.markdown(
                body_md,
                extensions=['tables', 'fenced_code', 'nl2br']
            )
            result.append(
                f'<div class="callout callout-{ctype.lower()}">'
                f'<div class="callout-title">{icon} {ctype}</div>'
                f'<div class="callout-body">{body_html}</div>'
                f'</div>'
            )
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)


# ---------------------------------------------------------------------------
# Build full HTML page
# ---------------------------------------------------------------------------
def md_to_html(md_text, title, eyebrow, subtitle, ribbon_text, footer_text):
    preprocessed = preprocess_callouts(md_text)

    body_html = markdown.markdown(
        preprocessed,
        extensions=['tables', 'fenced_code', 'nl2br'],
    )

    # Post-process: callout divs are already in body_html (inserted as raw HTML)
    # Remove the h1 that markdown generates from the # heading
    body_html = re.sub(r'^<h1>[^<]*</h1>\s*', '', body_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>{HTML_CSS}
  </style>
</head>
<body>
  <div class="page">
    <div class="doc-header">
      <div class="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p class='subtitle'>{subtitle}</p>
    </div>
    <div class="conf-ribbon">{ribbon_text}</div>
    <div class="content">
{body_html}
    </div>
    <div class="footer">{footer_text}</div>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Document definitions
# ---------------------------------------------------------------------------
DOCUMENTS = [
    {
        "md_file": "Wincham_ICAEW_Disciplinary_Referral.md",
        "html_file": "Wincham_ICAEW_Disciplinary_Referral.html",
        "title": "ICAEW Disciplinary Referral: Leonard Edward Jones — Adrem Accounting Ltd",
        "eyebrow": "Professional Conduct Referral — Institute of Chartered Accountants in England and Wales",
        "subtitle": "Formal disciplinary complaint concerning independence, objectivity, NOCLAR, and systematic SIC mis-classification",
        "ribbon": "⚠ STRICTLY CONFIDENTIAL — DRAFT FOR SOLICITOR REVIEW PRIOR TO SUBMISSION",
        "footer": "This draft referral was prepared by Dean Harrison as agent for Philip Harrison. Review by instructed solicitors required before submission to ICAEW. All Companies House data verified 1 April 2026.",
    },
    {
        "md_file": "Wincham_Legitimate_Interests_Assessment.md",
        "html_file": "Wincham_Legitimate_Interests_Assessment.html",
        "title": "Legitimate Interests Assessment — Wincham Victim Database",
        "eyebrow": "Internal Compliance Document — UK GDPR Article 6(1)(f)",
        "subtitle": "Three-part test documenting the lawful basis for assembly, storage, and disclosure of the Wincham Victim Database to regulated UK legal practitioners",
        "ribbon": "⚠ STRICTLY PRIVATE & CONFIDENTIAL — INTERNAL COMPLIANCE DOCUMENT — LIA-WINCHAM-001",
        "footer": "Document reference: LIA-WINCHAM-001 | Version 1.0 | April 2026. Prepared in accordance with ICO guidance on Legitimate Interests. Not legal advice — seek independent advice before disclosure.",
    },
    {
        "md_file": "Wincham_Nine_Task_Verification_Report.md",
        "html_file": "Wincham_Nine_Task_Verification_Report.html",
        "title": "Wincham Scheme — Nine-Task Regulatory Verification Report",
        "eyebrow": "Forensic Regulatory Evidence Report — Cross-Registry Verification",
        "subtitle": "Cross-registry forensic evidence of unauthorised operation — HMRC, ICAEW, ACCA, FCA, Companies House, Spanish registries",
        "ribbon": "⚠ ATTORNEY-CLIENT PRIVILEGED WORK PRODUCT — STRICTLY CONFIDENTIAL — NOT FOR DISCLOSURE WITHOUT AUTHORISATION",
        "footer": "Prepared by Dean Harrison (forensic research) — 1 April 2026. Attorney-client privileged work product. All data obtained from live public registers. For use by instructed solicitors only.",
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import os

    for doc in DOCUMENTS:
        md_path = os.path.join(BASE_DIR, doc["md_file"])
        html_path = os.path.join(BASE_DIR, doc["html_file"])

        print(f"\nProcessing: {doc['md_file']}")

        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        html = md_to_html(
            md_text=md_text,
            title=doc["title"],
            eyebrow=doc["eyebrow"],
            subtitle=doc["subtitle"],
            ribbon_text=doc["ribbon"],
            footer_text=doc["footer"],
        )

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        size_kb = os.path.getsize(html_path) // 1024
        print(f"  Written: {html_path}  ({size_kb} KB)")

    print("\nAll done.")


if __name__ == "__main__":
    main()
