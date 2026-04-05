r"""
generate_all_pdfs.py
Converts all Wincham case markdown documents to professionally styled PDFs.
Run from: c:\DAD\UK_Lanzarote_Repatriation
"""

import markdown
import re
import sys
from pathlib import Path

PDF_DIR = Path(r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham Scheme-Legal Claims-Victims')

DOCS = [
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_For_Law_Firms.md',
        'output': PDF_DIR / 'Wincham_Pitch_Report_For_Law_Firms.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_pitch_internal.html',
        'title': 'The Wincham Group Litigation Opportunity — Internal Pitch Report',
        'subtitle': 'A Commercial Pitch to UK Professional Negligence Law Firms',
        'eyebrow': 'STRICTLY PRIVATE & CONFIDENTIAL',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_EXTERNAL.md',
        'output': PDF_DIR / 'Wincham_Pitch_Report_EXTERNAL.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_pitch_external.html',
        'title': 'The Wincham Group Litigation Opportunity',
        'subtitle': 'External Commercial Pitch — Law Firm & CMC Edition',
        'eyebrow': 'STRICTLY PRIVATE & CONFIDENTIAL — NOT FOR DISTRIBUTION',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Ellis_Briefing_Document.md',
        'output': PDF_DIR / 'Ellis_Briefing_Document.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_ellis.html',
        'title': 'Ellis Harrison — Full Operational Briefing',
        'subtitle': 'Project: Wincham Group Litigation Data Programme',
        'eyebrow': 'PRIVATE & CONFIDENTIAL — FOR ADDRESSEE ONLY',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Legal_Lead_Generation_Business_Plan.md',
        'output': PDF_DIR / 'Wincham_Legal_Lead_Generation_Business_Plan.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_bplan.html',
        'title': 'The Wincham Litigation Lead Generation Playbook',
        'subtitle': 'Executive Strategy & Business Operations Report',
        'eyebrow': 'CONFIDENTIAL OPERATIONS REPORT',
        'ribbon': False,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Public_Evidence_Dossier.md',
        'output': PDF_DIR / 'Wincham_Public_Evidence_Dossier.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_evidence.html',
        'title': 'Wincham Group — Public Evidence Dossier',
        'subtitle': 'Forensic Evidence Compilation for Professional Negligence Proceedings',
        'eyebrow': 'PRIVILEGED & CONFIDENTIAL — LITIGATION SUPPORT',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Nine_Task_Verification_Report.md',
        'output': PDF_DIR / 'Wincham_Nine_Task_Verification_Report.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_nime_report.html',
        'title': 'Wincham Scheme — Nine-Task Regulatory Verification Report',
        'subtitle': 'Cross-Registry Forensic Evidence of Unauthorised Operation — April 2026',
        'eyebrow': 'ATTORNEY-CLIENT PRIVILEGED WORK PRODUCT — NOT FOR DISCLOSURE',
        'ribbon': True,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_ICAEW_Disciplinary_Referral.md',
        'output': PDF_DIR / 'Wincham_ICAEW_Disciplinary_Referral.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_icaew_referral.html',
        'title': 'ICAEW Formal Disciplinary Referral — Leonard Edward Jones',
        'subtitle': 'Complaint under the ICAEW Code of Ethics and NOCLAR Framework',
        'eyebrow': 'FORMAL REGULATORY COMPLAINT — ICAEW PROFESSIONAL STANDARDS',
        'ribbon': False,
    },
    {
        'input': r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_FCA_Referral.md',
        'output': PDF_DIR / 'Wincham_FCA_Referral.pdf',
        'html_tmp': r'C:\DAD\UK_Lanzarote_Repatriation\_tmp_fca_referral.html',
        'title': 'FCA Formal Referral — Wincham Group Unauthorised Regulated Activity',
        'subtitle': 'Suspected breach of FSMA 2000 s.19 — Financial Intermediation Without Authorisation',
        'eyebrow': 'FORMAL REGULATORY REFERRAL — FINANCIAL CONDUCT AUTHORITY',
        'ribbon': False,
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
    icon, border, bg, text = ALERT_ICONS.get(kind, ('📌', '#333', '#f5f5f5', '#333'))
    body_html = markdown.markdown(body)
    return (
        f'<div class="alert alert-{kind.lower()}" style="border-left:4px solid {border};'
        f'background:{bg};padding:14px 18px;margin:20px 0;border-radius:0 6px 6px 0;">'
        f'<div style="color:{border};font-weight:700;margin-bottom:6px;">{icon} {kind}</div>'
        f'<div style="color:{text};font-size:14px;">{body_html}</div></div>'
    )

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; font-size: 15px; line-height: 1.75; color: #1e1e2e; background: #f0f2f8; }
.page { max-width: 920px; margin: 0 auto; background: #ffffff; padding: 0 0 80px; box-shadow: 0 4px 40px rgba(0,0,0,0.10); min-height: 100vh; }
.doc-header { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; padding: 52px 60px 44px; }
.doc-header .eyebrow { font-size: 11px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: #94a3b8; margin-bottom: 14px; }
.doc-header h1 { font-size: 2.2em; font-weight: 700; line-height: 1.2; color: #fff; margin-bottom: 10px; }
.doc-header .subtitle { font-size: 1em; color: #cbd5e1; margin-bottom: 28px; }
.conf-ribbon { background: #c5221f; color: #fff; text-align: center; padding: 10px; font-size: 11px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; }
.content { padding: 48px 60px; }
h2 { font-size: 1.15em; font-weight: 700; color: #0f0c29; margin: 44px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #e8eaf6; text-transform: uppercase; letter-spacing: 0.5px; }
h3 { font-size: 1em; font-weight: 600; color: #302b63; margin: 28px 0 10px; }
h4 { font-size: 0.95em; font-weight: 600; color: #555; margin: 20px 0 8px; }
p { margin-bottom: 14px; }
ul, ol { margin: 10px 0 14px 22px; }
li { margin-bottom: 6px; }
strong { color: #0f0c29; }
table { width: 100%; border-collapse: collapse; margin: 20px 0 28px; font-size: 13.5px; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 6px rgba(0,0,0,0.06); }
thead th { background: #302b63; color: #fff; padding: 11px 16px; text-align: left; font-weight: 600; font-size: 12.5px; }
tbody td { padding: 10px 16px; border-bottom: 1px solid #eef0f8; vertical-align: top; }
tbody tr:nth-child(even) { background: #f8f9ff; }
tbody tr:last-child td { border-bottom: none; }
blockquote { border-left: 4px solid #302b63; background: #f0f2f8; padding: 14px 18px; margin: 18px 0; border-radius: 0 6px 6px 0; color: #302b63; font-style: italic; font-size: 14px; }
hr { border: none; border-top: 1px solid #eef0f8; margin: 36px 0; }
.footer { margin: 0 60px; padding-top: 20px; border-top: 1px solid #eef0f8; font-size: 11.5px; color: #94a3b8; line-height: 1.6; }
a { color: #302b63; }
@media print { body { background: white; } .page { box-shadow: none; } }
"""

def build_html(doc, body_html):
    ribbon = '<div class="conf-ribbon">⚠ STRICTLY PRIVATE &amp; CONFIDENTIAL — NOT FOR DISTRIBUTION</div>' if doc['ribbon'] else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc['title']}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="page">
    <div class="doc-header">
      <div class="eyebrow">{doc['eyebrow']}</div>
      <h1>{doc['title']}</h1>
      <div class="subtitle">{doc['subtitle']}</div>
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
  </div>
</body>
</html>"""

def md_to_html(md_text):
    md_text = re.sub(
        r'> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n((?:> .*\n?)*)',
        replace_alert, md_text
    )
    return markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])

# Try to import pdfkit or weasyprint
pdf_engine = None
try:
    import pdfkit
    pdf_engine = 'pdfkit'
    print("Using pdfkit for PDF generation")
except ImportError:
    pass

if pdf_engine is None:
    try:
        from weasyprint import HTML as WP_HTML
        pdf_engine = 'weasyprint'
        print("Using weasyprint for PDF generation")
    except ImportError:
        pass

if pdf_engine is None:
    print("ERROR: Neither pdfkit nor weasyprint is installed.")
    print("Install one of:")
    print("  pip install pdfkit   (also requires wkhtmltopdf)")
    print("  pip install weasyprint")
    sys.exit(1)

print(f"\nGenerating {len(DOCS)} documents...\n")
for doc in DOCS:
    print(f"Processing: {Path(doc['input']).name}")
    raw = Path(doc['input']).read_text(encoding='utf-8')
    body_html = md_to_html(raw)
    html_content = build_html(doc, body_html)

    # Always write a print-ready HTML file to the output folder
    html_out_path = Path(str(doc['output'])).with_suffix('.html')
    html_out_path.parent.mkdir(parents=True, exist_ok=True)
    html_out_path.write_text(html_content, encoding='utf-8')
    print(f"  ✅ HTML written: {html_out_path}")

    # Attempt PDF generation if engine available
    out_path = str(doc['output'])
    if pdf_engine == 'pdfkit':
        # Also write temp file for pdfkit
        tmp_path = doc['html_tmp']
        Path(tmp_path).write_text(html_content, encoding='utf-8')
        try:
            opts = {
                'page-size': 'A4',
                'margin-top': '0',
                'margin-right': '0',
                'margin-bottom': '0',
                'margin-left': '0',
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
            }
            import pdfkit
            pdfkit.from_file(tmp_path, out_path, options=opts)
            print(f"  ✅ PDF written: {out_path}")
        except Exception as e:
            print(f"  ⚠️  PDF skipped (open HTML in browser → Ctrl+P → Save as PDF): {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    elif pdf_engine == 'weasyprint':
        try:
            from weasyprint import HTML as WP_HTML
            WP_HTML(filename=str(html_out_path)).write_pdf(out_path)
            print(f"  ✅ PDF written: {out_path}")
        except Exception as e:
            print(f"  ⚠️  PDF skipped (open HTML in browser → Ctrl+P → Save as PDF): {e}")

    else:
        print(f"  ℹ️  No PDF engine — open HTML in browser → Ctrl+P → Save as PDF")

print("\nDone.\n")
print(f"HTML files are in: {PDF_DIR}")
print("To generate PDFs: open each HTML file in Chrome and press Ctrl+P → Save as PDF → A4, No margins")

