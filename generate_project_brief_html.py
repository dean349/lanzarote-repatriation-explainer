"""
Generate a polished HTML version of the Philip Harrison Project Brief.
Reads from the Antigravity brain artifact and outputs a standalone HTML file
that Philip can open in any browser.
"""

import re
import sys
from pathlib import Path
from datetime import datetime

BRIEF_PATH = Path(r"C:\Users\Dean Harrison\.gemini\antigravity\brain\4975232e-60ac-439b-90ba-92845263c8dd\project_brief.md")
OUTPUT_PATH = Path(r"c:\DAD\UK_Lanzarote_Repatriation\Files and Information for Phil Harrison\Philip_Harrison_Project_Brief.html")


def md_to_html(md: str) -> str:
    """Lightweight markdown-to-HTML converter for the brief."""

    lines = md.split("\n")
    html_parts = []
    in_table = False
    in_ul = False
    in_ol = False
    i = 0

    def inline(text):
        """Process inline markdown."""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # strip local file links
        # External links
        text = re.sub(r'https?://\S+', lambda m: f'<a href="{m.group()}" target="_blank">{m.group()}</a>', text)
        return text

    def close_lists():
        parts = []
        nonlocal in_ul, in_ol
        if in_ul:
            parts.append("</ul>")
            in_ul = False
        if in_ol:
            parts.append("</ol>")
            in_ol = False
        return parts

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            html_parts.extend(close_lists())
            if in_table:
                html_parts.append("</tbody></table>")
                in_table = False
            html_parts.append('<hr>')
            i += 1
            continue

        # Alert blockquotes  [!NOTE] etc
        if stripped.startswith("> [!"):
            html_parts.extend(close_lists())
            alert_type = re.match(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', stripped)
            atype = alert_type.group(1).lower() if alert_type else "note"
            labels = {"note": "📝 Note", "tip": "💡 Tip", "important": "⚠️ Important", "warning": "⚠️ Warning", "caution": "🚨 Caution"}
            colors = {"note": "#1e3a5f", "tip": "#1a3d2b", "important": "#3d2a00", "warning": "#3d2a00", "caution": "#3d1a1a"}
            borders = {"note": "#3b82f6", "tip": "#22c55e", "important": "#f59e0b", "warning": "#f59e0b", "caution": "#ef4444"}
            # Collect continuation lines
            content_lines = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                content_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            content = " ".join(content_lines)
            html_parts.append(f'''<div class="alert alert-{atype}" style="background:{colors[atype]};border-left:4px solid {borders[atype]};padding:14px 18px;border-radius:6px;margin:16px 0;">
<strong style="color:{borders[atype]}">{labels[atype]}</strong><br>
<span>{inline(content)}</span>
</div>''')
            continue

        # Regular blockquote
        if stripped.startswith(">"):
            html_parts.extend(close_lists())
            content = stripped.lstrip(">").strip()
            html_parts.append(f'<blockquote>{inline(content)}</blockquote>')
            i += 1
            continue

        # Table rows
        if "|" in stripped and stripped.startswith("|"):
            if in_ul or in_ol:
                html_parts.extend(close_lists())
            # Check if separator row
            if re.match(r'^\|[\s\-|:]+\|$', stripped):
                i += 1
                continue
            if not in_table:
                html_parts.append('<div class="table-wrap"><table>')
                # First row = header
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                html_parts.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                in_table = True
            else:
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                html_parts.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            i += 1
            continue
        elif in_table:
            html_parts.append("</tbody></table></div>")
            in_table = False

        # Headings
        if stripped.startswith("# "):
            html_parts.extend(close_lists())
            text = stripped[2:]
            slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            html_parts.append(f'<h1 id="{slug}">{inline(text)}</h1>')
            i += 1
            continue
        if stripped.startswith("## "):
            html_parts.extend(close_lists())
            text = stripped[3:]
            slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            html_parts.append(f'<h2 id="{slug}">{inline(text)}</h2>')
            i += 1
            continue
        if stripped.startswith("### "):
            html_parts.extend(close_lists())
            text = stripped[4:]
            slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            html_parts.append(f'<h3 id="{slug}">{inline(text)}</h3>')
            i += 1
            continue
        if stripped.startswith("#### "):
            html_parts.extend(close_lists())
            text = stripped[5:]
            html_parts.append(f'<h4>{inline(text)}</h4>')
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if ol_match:
            if in_ul:
                html_parts.extend(close_lists())
            if not in_ol:
                html_parts.append("<ol>")
                in_ol = True
            html_parts.append(f"<li>{inline(ol_match.group(2))}</li>")
            i += 1
            continue

        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            if in_ol:
                html_parts.extend(close_lists())
            if not in_ul:
                html_parts.append("<ul>")
                in_ul = True
            html_parts.append(f"<li>{inline(stripped[2:])}</li>")
            i += 1
            continue

        # Empty line
        if not stripped:
            html_parts.extend(close_lists())
            if in_table:
                html_parts.append("</tbody></table></div>")
                in_table = False
            i += 1
            continue

        # Regular paragraph
        html_parts.extend(close_lists())
        if in_table:
            html_parts.append("</tbody></table></div>")
            in_table = False
        html_parts.append(f"<p>{inline(stripped)}</p>")
        i += 1

    html_parts.extend(close_lists())
    if in_table:
        html_parts.append("</tbody></table></div>")

    return "\n".join(html_parts)


def build_toc(md: str) -> str:
    """Build table of contents from H2/H3 headings."""
    items = []
    for line in md.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            text = stripped[3:]
            slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            items.append(f'<li class="toc-h2"><a href="#{slug}">{text}</a></li>')
        elif stripped.startswith("### "):
            text = stripped[4:]
            slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            items.append(f'<li class="toc-h3"><a href="#{slug}">{text}</a></li>')
    return "\n".join(items)


def build_html(md_content: str) -> str:
    body = md_to_html(md_content)
    toc = build_toc(md_content)
    date_str = datetime.now().strftime("%d %B %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Philip Harrison — Lanzarote Case Brief</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #1f2937;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --accent: #c9955c;
    --accent2: #58a6ff;
    --gold: #f0c14b;
    --red: #f85149;
    --green: #3fb950;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.8;
    font-size: 15px;
  }}

  /* ── HEADER ── */
  .site-header {{
    background: linear-gradient(135deg, #0d1117 0%, #1a1000 50%, #0d1117 100%);
    border-bottom: 1px solid #c9955c44;
    padding: 48px 32px 36px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }}
  .site-header::before {{
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 0%, #c9955c18 0%, transparent 70%);
  }}
  .header-badge {{
    display: inline-block;
    background: #c9955c22;
    border: 1px solid #c9955c55;
    color: var(--accent);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 16px;
  }}
  .site-header h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(26px, 4vw, 42px);
    font-weight: 700;
    color: #fff;
    margin-bottom: 10px;
    position: relative;
  }}
  .site-header h1 span {{ color: var(--accent); }}
  .header-sub {{
    color: var(--text-muted);
    font-size: 14px;
    max-width: 600px;
    margin: 0 auto 20px;
    position: relative;
  }}
  .header-meta {{
    display: flex;
    justify-content: center;
    gap: 24px;
    flex-wrap: wrap;
    position: relative;
  }}
  .header-meta span {{
    background: #ffffff0d;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 12px;
    color: var(--text-muted);
  }}
  .header-meta strong {{ color: var(--accent); }}

  /* ── LAYOUT ── */
  .layout {{
    display: flex;
    max-width: 1280px;
    margin: 0 auto;
    gap: 0;
  }}
  .sidebar {{
    width: 280px;
    flex-shrink: 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 24px 0;
  }}
  .sidebar-title {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0 20px 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
  }}
  .toc-list {{ list-style: none; padding: 0; }}
  .toc-list li {{ line-height: 1; }}
  .toc-h2 a {{
    display: block;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-decoration: none;
    border-left: 2px solid transparent;
    transition: all 0.2s;
  }}
  .toc-h2 a:hover {{ color: var(--accent); border-left-color: var(--accent); background: #c9955c0a; }}
  .toc-h3 a {{
    display: block;
    padding: 5px 20px 5px 32px;
    font-size: 11px;
    color: #6e7681;
    text-decoration: none;
    transition: color 0.2s;
  }}
  .toc-h3 a:hover {{ color: var(--text-muted); }}

  .main-content {{
    flex: 1;
    min-width: 0;
    padding: 40px 48px;
    max-width: 860px;
  }}

  /* ── TYPOGRAPHY ── */
  h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    color: #fff;
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px;
    margin: 40px 0 20px;
  }}
  h1:first-child {{ margin-top: 0; }}
  h2 {{
    font-size: 20px;
    font-weight: 700;
    color: var(--accent);
    margin: 36px 0 14px;
    padding: 12px 16px;
    background: #c9955c0d;
    border-left: 3px solid var(--accent);
    border-radius: 0 6px 6px 0;
  }}
  h3 {{
    font-size: 16px;
    font-weight: 600;
    color: #e2e8f0;
    margin: 24px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }}
  h4 {{
    font-size: 14px;
    font-weight: 600;
    color: var(--accent2);
    margin: 18px 0 8px;
  }}
  p {{ margin: 10px 0; color: var(--text); }}
  strong {{ color: #fff; font-weight: 600; }}
  em {{ color: var(--text-muted); font-style: italic; }}
  code {{
    background: #ffffff12;
    border: 1px solid var(--border);
    padding: 1px 6px;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    color: #79c0ff;
  }}
  a {{ color: var(--accent2); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 32px 0;
  }}
  blockquote {{
    background: #58a6ff0d;
    border-left: 3px solid var(--accent2);
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin: 16px 0;
    color: var(--text-muted);
    font-style: italic;
  }}
  ul, ol {{ padding-left: 22px; margin: 10px 0; }}
  ul li, ol li {{ margin: 5px 0; }}

  /* ── TABLES ── */
  .table-wrap {{ overflow-x: auto; margin: 16px 0; border-radius: 8px; border: 1px solid var(--border); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{
    background: var(--surface2);
    color: var(--accent);
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  td {{
    padding: 10px 14px;
    border-bottom: 1px solid #21262d;
    color: var(--text);
    vertical-align: top;
  }}
  tr:last-child td {{ border-bottom: none; }}
  tr:nth-child(even) td {{ background: #ffffff04; }}
  tr:hover td {{ background: #c9955c08; }}

  /* ── ALERTS ── */
  .alert {{ border-radius: 8px !important; font-size: 14px; }}

  /* ── PERSON CARDS ── */
  h4:has(+ p) {{ margin-bottom: 4px; }}

  /* ── FOOTER ── */
  .site-footer {{
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 24px 32px;
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
  }}
  .site-footer strong {{ color: var(--accent); }}

  /* ── PRINT ── */
  @media print {{
    .sidebar {{ display: none; }}
    .main-content {{ padding: 20px; max-width: 100%; }}
    h2 {{ background: none; border-left: 3px solid #000; color: #000; }}
    body {{ background: #fff; color: #000; }}
  }}

  /* ── RESPONSIVE ── */
  @media (max-width: 900px) {{
    .sidebar {{ display: none; }}
    .main-content {{ padding: 24px 20px; }}
  }}
</style>
</head>
<body>

<header class="site-header">
  <div class="header-badge">Confidential — Attorney-Client Privileged</div>
  <h1>Philip Harrison — <span>Lanzarote Case Brief</span></h1>
  <p class="header-sub">A complete plain-English guide to everything Dean has done: the Spanish taxes, the company wind-down, and the legal case against Wincham Accountants.</p>
  <div class="header-meta">
    <span>Prepared by <strong>Dean Harrison</strong></span>
    <span>Date: <strong>{date_str}</strong></span>
    <span>Case Ref: <strong>Los Romeros Ltd / Philip Harrison</strong></span>
    <span>Classification: <strong>Private &amp; Confidential</strong></span>
  </div>
</header>

<div class="layout">
  <nav class="sidebar">
    <div class="sidebar-title">Contents</div>
    <ul class="toc-list">
{toc}
    </ul>
  </nav>
  <main class="main-content">
{body}
  </main>
</div>

<footer class="site-footer">
  <p>Prepared by <strong>Dean Harrison</strong> on behalf of Philip Harrison &bull; {date_str}<br>
  This document is private and confidential. It is intended solely for Philip Harrison and his legal representatives.<br>
  <em>This is not legal advice. All figures should be verified with a qualified solicitor and tax adviser before action is taken.</em></p>
</footer>

</body>
</html>"""


def main():
    print(f"Reading brief from: {BRIEF_PATH}")
    if not BRIEF_PATH.exists():
        print(f"ERROR: Brief not found at {BRIEF_PATH}")
        sys.exit(1)

    md_content = BRIEF_PATH.read_text(encoding="utf-8")
    print(f"Brief loaded: {len(md_content):,} characters, {md_content.count(chr(10)):,} lines")

    print("Converting to HTML...")
    html = build_html(md_content)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"\n✅ HTML written successfully:")
    print(f"   Path : {OUTPUT_PATH}")
    print(f"   Size : {size_kb:.1f} KB")
    print(f"\nPhilip can open this file directly in any web browser.")


if __name__ == "__main__":
    main()
