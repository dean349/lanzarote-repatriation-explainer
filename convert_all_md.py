"""
Convert all .md files in the Wincham Legal Case folder to styled HTML.
Applies different themes based on filename keyword detection.
"""
import os, re, markdown

FOLDER = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"

# ── Alert block renderer ──────────────────────────────────────────────────────
ALERT_ICONS = {
    'NOTE':      ('ℹ️',  '#1a73e8', '#e8f0fe', '#174ea6'),
    'TIP':       ('💡',  '#1e8e3e', '#e6f4ea', '#137333'),
    'IMPORTANT': ('❗',  '#e37400', '#fef3e2', '#b45309'),
    'WARNING':   ('⚠️',  '#c77700', '#fef9e7', '#92400e'),
    'CAUTION':   ('🔴',  '#c5221f', '#fce8e6', '#a50e0e'),
}

def render_alerts(raw):
    def _replace(m):
        kind = m.group(1).upper()
        body = m.group(2).strip().replace('\n> ', '\n')
        icon, border, bg, text = ALERT_ICONS.get(kind, ('📌','#333','#f5f5f5','#333'))
        body_html = markdown.markdown(body)
        return (
            f'<div class="alert alert-{kind.lower()}" style="border-left:4px solid {border};'
            f'background:{bg};padding:14px 18px;margin:20px 0;border-radius:0 6px 6px 0;">'
            f'<div style="color:{border};font-weight:700;margin-bottom:6px;">{icon} {kind}</div>'
            f'<div style="color:{text};font-size:14px;">{body_html}</div></div>'
        )
    return re.sub(r'> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n((?:> .*\n?)*)', _replace, raw)

# ── Theme definitions ─────────────────────────────────────────────────────────
def theme_legal(title):
    """Formal legal / NDA theme — dark charcoal, serif feel."""
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap');
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'EB Garamond',Georgia,serif;font-size:16px;line-height:1.8;color:#1a1a1a;background:#f5f0e8}}
    .page{{max-width:860px;margin:0 auto;background:#fff;padding:0 0 80px;box-shadow:0 4px 40px rgba(0,0,0,.15);min-height:100vh}}
    .doc-header{{background:#1a1a2e;color:#fff;padding:52px 60px 44px}}
    .doc-header .eyebrow{{font-family:'Inter',sans-serif;font-size:10px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#94a3b8;margin-bottom:14px}}
    .doc-header h1{{font-size:1.9em;font-weight:600;line-height:1.25;color:#fff;margin-bottom:8px}}
    .doc-header .subtitle{{font-size:0.9em;font-family:'Inter',sans-serif;color:#cbd5e1}}
    .conf-ribbon{{background:#8b0000;color:#fff;text-align:center;padding:10px;font-family:'Inter',sans-serif;font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase}}
    .content{{padding:52px 60px}}
    h2{{font-size:1em;font-weight:600;font-family:'Inter',sans-serif;color:#1a1a2e;margin:44px 0 12px;padding-bottom:8px;border-bottom:2px solid #e8e0d0;text-transform:uppercase;letter-spacing:1px}}
    h3{{font-size:1em;font-weight:600;font-family:'Inter',sans-serif;color:#555;margin:28px 0 10px}}
    p{{margin-bottom:14px}}
    ul,ol{{margin:10px 0 14px 24px}}
    li{{margin-bottom:6px}}
    strong{{color:#1a1a2e}}
    table{{width:100%;border-collapse:collapse;margin:20px 0 28px;font-size:14px;font-family:'Inter',sans-serif}}
    thead th{{background:#1a1a2e;color:#fff;padding:10px 16px;text-align:left;font-weight:600;font-size:12px}}
    tbody td{{padding:10px 16px;border-bottom:1px solid #eee;vertical-align:top}}
    tbody tr:nth-child(even){{background:#faf8f4}}
    tbody tr:last-child td{{border-bottom:none}}
    blockquote{{border-left:4px solid #1a1a2e;background:#f5f0e8;padding:14px 18px;margin:18px 0;border-radius:0 4px 4px 0;font-style:italic;font-size:15px;color:#333}}
    hr{{border:none;border-top:1px solid #e8e0d0;margin:36px 0}}
    .sig-block{{background:#faf8f4;border:1px solid #e8e0d0;border-radius:6px;padding:24px 28px;margin:28px 0}}
    .footer{{margin:0 60px;padding-top:20px;border-top:1px solid #e8e0d0;font-family:'Inter',sans-serif;font-size:11px;color:#999;line-height:1.6}}
    @media(max-width:700px){{.doc-header,.content{{padding:28px 20px}}.footer{{margin:0 20px}}}}
    @media print{{body{{background:#fff}}.page{{box-shadow:none}}}}
    """

def theme_pitch(title):
    """Premium pitch / business document theme — navy/purple gradient."""
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Inter','Segoe UI',system-ui,sans-serif;font-size:15px;line-height:1.75;color:#1e1e2e;background:#f0f2f8}}
    .page{{max-width:920px;margin:0 auto;background:#fff;padding:0 0 80px;box-shadow:0 4px 40px rgba(0,0,0,.10);min-height:100vh}}
    .doc-header{{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:#fff;padding:52px 60px 44px}}
    .doc-header .eyebrow{{font-size:11px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#94a3b8;margin-bottom:14px}}
    .doc-header h1{{font-size:2.2em;font-weight:700;line-height:1.2;color:#fff;margin-bottom:10px}}
    .doc-header .subtitle{{font-size:1em;color:#cbd5e1;margin-bottom:8px}}
    .conf-ribbon{{background:#c5221f;color:#fff;text-align:center;padding:10px;font-size:11px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase}}
    .content{{padding:48px 60px}}
    h2{{font-size:1.05em;font-weight:700;color:#0f0c29;margin:44px 0 12px;padding-bottom:8px;border-bottom:2px solid #e8eaf6;text-transform:uppercase;letter-spacing:.5px}}
    h3{{font-size:1em;font-weight:600;color:#302b63;margin:28px 0 10px}}
    h4{{font-size:.95em;font-weight:600;color:#555;margin:20px 0 8px}}
    p{{margin-bottom:14px}}
    ul,ol{{margin:10px 0 14px 22px}}
    li{{margin-bottom:6px}}
    strong{{color:#0f0c29}}
    table{{width:100%;border-collapse:collapse;margin:20px 0 28px;font-size:13.5px;border-radius:8px;overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.06)}}
    thead th{{background:#302b63;color:#fff;padding:11px 16px;text-align:left;font-weight:600;font-size:12.5px}}
    tbody td{{padding:10px 16px;border-bottom:1px solid #eef0f8;vertical-align:top}}
    tbody tr:nth-child(even){{background:#f8f9ff}}
    tbody tr:last-child td{{border-bottom:none}}
    blockquote{{border-left:4px solid #302b63;background:#f0f2f8;padding:14px 18px;margin:18px 0;border-radius:0 6px 6px 0;color:#302b63;font-style:italic;font-size:14px}}
    hr{{border:none;border-top:1px solid #eef0f8;margin:36px 0}}
    .footer{{margin:0 60px;padding-top:20px;border-top:1px solid #eef0f8;font-size:11.5px;color:#94a3b8;line-height:1.6}}
    @media(max-width:700px){{.doc-header,.content{{padding:28px 20px}}.footer{{margin:0 20px}}}}
    @media print{{body{{background:#fff}}.page{{box-shadow:none}}}}
    """

# ── File metadata ─────────────────────────────────────────────────────────────
FILE_META = {
    "Wincham_Pitch_Report_EXTERNAL": {
        "eyebrow": "Strictly Private & Confidential — Professional Negligence Group Litigation",
        "title": "The Wincham Group Litigation Opportunity",
        "subtitle": "External Commercial Pitch — For Distribution Under Executed NDA Only",
        "ribbon": "⚠ Strictly Private & Confidential — Execute NDA Before Reading Further",
        "footer": ("This document is provided under the terms of the executed Non-Disclosure and "
                   "Non-Circumvention Agreement. Distribution is strictly prohibited. "
                   "All quantum figures are estimates pending formal legal review."),
        "theme": "pitch",
    },
    "Wincham_NDA_Non_Circumvention": {
        "eyebrow": "Legal Agreement — Execute Before Any Information Exchange",
        "title": "Non-Disclosure, Non-Circumvention & Non-Solicitation Agreement",
        "subtitle": "Wincham Group Litigation — Introducing Consultant & Law Firm Partner",
        "ribbon": "⚠ EXECUTE AND RETURN THIS AGREEMENT BEFORE ANY FURTHER DISCLOSURE",
        "footer": ("This agreement should be reviewed by a qualified solicitor before execution. "
                   "Jurisdiction: England & Wales. Governing law: English law."),
        "theme": "legal",
    },
    "Wincham_Legal_Lead_Generation_Business_Plan": {
        "eyebrow": "Internal Strategic Document — Do Not Distribute",
        "title": "Wincham Scheme: Legal Lead Generation Business Plan",
        "subtitle": "Operational guide for the Wincham victim database marketing programme",
        "ribbon": "⚠ INTERNAL USE ONLY — DO NOT SHARE WITH ANY THIRD PARTY",
        "footer": ("This document is for internal strategic planning purposes only. "
                   "It must not be disclosed to any law firm, claims company, or third party "
                   "prior to execution of a Non-Disclosure Agreement."),
        "theme": "pitch",
    },
    "Wincham_Pitch_Report_For_Law_Firms": {
        "eyebrow": "Internal Reference Copy — Full Methodology Version",
        "title": "The Wincham Group Litigation Opportunity",
        "subtitle": "Internal Working Document (Unredacted) — NOT for External Distribution",
        "ribbon": "⚠ INTERNAL VERSION — CONTAINS PROPRIETARY METHODOLOGY — DO NOT SHARE",
        "footer": ("Internal working document. Do not distribute. "
                   "Use Wincham_Pitch_Report_EXTERNAL.html for any external engagement."),
        "theme": "pitch",
    },
    "Wincham_Data_Licence_Agreement": {
        "eyebrow": "Commercial Contract — Execute After NDA and Price Agreement",
        "title": "Data Licence Agreement",
        "subtitle": "Dean Harrison (Licensor) and [Law Firm] (Licensee) — Wincham Victim Database",
        "ribbon": "⚠ STRICTLY PRIVATE & CONFIDENTIAL — COMMERCIAL CONTRACT",
        "footer": ("This agreement is governed by the law of England and Wales. "
                   "Both Parties should obtain independent legal advice before execution. "
                   "Prepared for commercial negotiation — all figures are indicative."),
        "theme": "legal",
    },
    "Dean_Ellis_Introduction_Fee_Agreement": {
        "eyebrow": "Private Agreement — Dean Harrison & Ellis Harrison Only",
        "title": "Commercial Introduction Fee Agreement",
        "subtitle": "Dean Harrison (Principal) and Ellis Harrison (Introducer) — For Internal Use Only",
        "ribbon": "⚠ PRIVATE & CONFIDENTIAL — DO NOT SHARE WITH ANY THIRD PARTY",
        "footer": ("This private agreement is between Dean Harrison and Ellis Harrison only. "
                   "It must not be disclosed to any law firm, claims company, or third party. "
                   "Governed by the law of England and Wales."),
        "theme": "legal",
    },
    "Ellis_Briefing_Document": {
        "eyebrow": "Private & Confidential — For Ellis Harrison Only",
        "title": "Wincham Group Litigation Data Programme",
        "subtitle": "Full Operational Briefing — From Dean Harrison",
        "ribbon": "⚠ PRIVATE & CONFIDENTIAL — FOR ADDRESSEE ONLY — DO NOT FORWARD OR COPY",
        "footer": ("This briefing is addressed solely to Ellis Harrison. "
                   "It must not be forwarded, copied, or shared with any third party. "
                   "Prepared by Dean Harrison — all commercial terms subject to written agreement."),
        "theme": "pitch",
    },
}

DEFAULT_META = {
    "eyebrow": "Wincham Group Litigation",
    "title": "",
    "subtitle": "",
    "ribbon": "⚠ Strictly Private & Confidential",
    "footer": "Wincham Group Litigation — Confidential Document",
    "theme": "pitch",
}

# ── HTML template ─────────────────────────────────────────────────────────────
def build_html(stem, body_html, meta):
    theme_fn = theme_legal if meta["theme"] == "legal" else theme_pitch
    css = theme_fn(meta["title"])
    title = meta["title"] or stem.replace("_", " ")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <div class="page">
    <div class="doc-header">
      <div class="eyebrow">{meta['eyebrow']}</div>
      <h1>{title}</h1>
      {"<p class='subtitle'>" + meta['subtitle'] + "</p>" if meta['subtitle'] else ""}
    </div>
    <div class="conf-ribbon">{meta['ribbon']}</div>
    <div class="content">
      {body_html}
    </div>
    <div class="footer">{meta['footer']}</div>
  </div>
</body>
</html>"""

# ── Main conversion loop ──────────────────────────────────────────────────────
md_files = [f for f in os.listdir(FOLDER) if f.lower().endswith('.md')]
print(f"Found {len(md_files)} Markdown file(s):\n")

for fname in sorted(md_files):
    stem = os.path.splitext(fname)[0]
    src  = os.path.join(FOLDER, fname)
    dst  = os.path.join(FOLDER, stem + ".html")

    # Read source
    with open(src, encoding='utf-8') as f:
        raw = f.read()

    # Strip the first H1 (we render it in the header band)
    raw = re.sub(r'^#\s+.+\n', '', raw, count=1)

    # Render alerts
    raw = render_alerts(raw)

    # Convert to HTML
    body_html = markdown.markdown(raw, extensions=['tables', 'fenced_code', 'toc'])

    # Get metadata
    meta = dict(DEFAULT_META)
    meta.update(FILE_META.get(stem, {}))
    if not meta["title"]:
        meta["title"] = stem.replace("_", " ")

    # Build and write HTML
    html = build_html(stem, body_html, meta)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = round(os.path.getsize(dst) / 1024, 1)
    print(f"  ✓  {fname}  →  {stem}.html  ({size_kb} KB)")

print("\nAll done.")
