import markdown
import os
import re

MD_FILE = r"C:\Users\Dean Harrison\.gemini\antigravity\brain\4975232e-60ac-439b-90ba-92845263c8dd\project_brief.md"
HTML_OUT = r"c:\DAD\UK_Lanzarote_Repatriation\project_brief.html"

def convert_md_to_html():
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert GitHub Alerts
    md_text = re.sub(r'> \[!IMPORTANT\](.*?)(\n>.*?)*', r'<div class="alert alert-red"><strong>🚨 IMPORTANT</strong>\1\2</div>', md_text, flags=re.MULTILINE|re.IGNORECASE)
    md_text = re.sub(r'> \[!NOTE\](.*?)(\n>.*?)*', r'<div class="alert alert-blue"><strong>📝 NOTE</strong>\1\2</div>', md_text, flags=re.MULTILINE|re.IGNORECASE)
    md_text = re.sub(r'> \[!CAUTION\](.*?)(\n>.*?)*', r'<div class="alert alert-amber"><strong>⚠️ CAUTION</strong>\1\2</div>', md_text, flags=re.MULTILINE|re.IGNORECASE)

    # Some basic cleanup of nested blockquotes from alerts if re couldn't fully catch
    md_text = md_text.replace('> ', '')

    # Convert mapping to markdown extension tables
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])

    # Style tweaks for tables that markdown outputs
    html_content = html_content.replace('<table>', '<div class="tbl-wrap"><table>')
    html_content = html_content.replace('</table>', '</table></div>')

    # Template
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Philip Harrison — Lanzarote Property Repatriation Project Brief</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
        :root {{
            --navy: #0f1e3c; --gold: #c9a84c; --gold-light: #f0d98c;
            --slate: #1e2d4a; --mid: #2d4168; --accent: #3a7bd5;
            --green: #27ae60; --red: #c0392b; --amber: #e67e22;
            --light: #f4f6fa; --white: #ffffff; --text: #1a1a2e; --muted: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--light); color: var(--text); line-height: 1.6; }}
        
        /* HEADER */
        header {{ background: linear-gradient(135deg, var(--navy) 0%, var(--slate) 60%, var(--mid) 100%);
            color: white; padding: 4rem 2rem; text-align: center; position: relative; overflow: hidden; }}
        header::before {{ content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(ellipse at 30% 50%, rgba(201,168,76,0.08) 0%, transparent 60%); pointer-events: none; }}
        .badge {{ display: inline-block; background: rgba(201,168,76,0.2); border: 1px solid var(--gold);
            color: var(--gold-light); padding: 0.4rem 1.2rem; border-radius: 20px; font-size: 0.85rem;
            letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1.5rem; font-weight: 600; }}
        header h1 {{ font-family: 'Playfair Display', serif; font-size: 2.8rem; line-height: 1.2; margin-bottom: 1rem; }}
        .subtitle {{ color: rgba(255,255,255,0.8); font-size: 1.1rem; max-width: 600px; margin: 0 auto; }}

        /* LAYOUT */
        .container {{ max-width: 1000px; margin: 0 auto; padding: 3rem 1.5rem; }}
        
        /* CONTENT STYLING */
        h1, h2, h3, h4, h5 {{ color: var(--navy); margin-top: 2rem; margin-bottom: 1rem; font-weight: 600; }}
        h2 {{ font-family: 'Playfair Display', serif; font-size: 2rem; border-bottom: 2px solid var(--gold); padding-bottom: 0.5rem; margin-top: 3rem; }}
        h3 {{ font-size: 1.5rem; color: var(--mid); margin-top: 2.5rem; }}
        h4 {{ font-size: 1.2rem; color: var(--accent); }}
        
        p {{ margin-bottom: 1.2rem; }}
        ul, ol {{ margin-bottom: 1.5rem; padding-left: 1.5rem; }}
        li {{ margin-bottom: 0.5rem; }}
        
        a {{ color: var(--accent); text-decoration: none; font-weight: 500; transition: color 0.2s; }}
        a:hover {{ color: var(--navy); text-decoration: underline; }}
        
        blockquote {{ border-left: 4px solid var(--gold); padding-left: 1.5rem; margin-left: 0; margin-bottom: 2rem; font-style: italic; color: var(--muted); }}
        
        hr {{ border: 0; height: 1px; background: #e2e8f0; margin: 3rem 0; }}

        /* ALERT BOXES */
        .alert {{ border-radius: 8px; padding: 1.5rem; margin: 2rem 0; border-left: 5px solid; }}
        .alert-red {{ background: #fef2f2; border-color: var(--red); color: #7f1d1d; }}
        .alert-amber {{ background: #fffbeb; border-color: var(--amber); color: #78350f; }}
        .alert-green {{ background: #f0fdf4; border-color: var(--green); color: #14532d; }}
        .alert-blue {{ background: #eff6ff; border-color: var(--accent); color: #1e3a5f; }}
        .alert strong {{ display: block; margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }}

        /* TABLES */
        .tbl-wrap {{ overflow-x: auto; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin: 2rem 0; border: 1px solid #e2e8f0; }}
        table {{ width: 100%; border-collapse: collapse; background: white; font-size: 0.9rem; }}
        th {{ background: var(--navy); color: white; padding: 1rem 1.2rem; text-align: left; font-weight: 600;
            font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap; }}
        td {{ padding: 1rem 1.2rem; border-bottom: 1px solid #f1f5f9; color: #374151; vertical-align: top; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #f8fafc; }}

        /* CHIPS (if needed in HTML) */
        .chip {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }}
        
        footer {{ background: var(--navy); color: rgba(255,255,255,0.5); text-align: center; padding: 2rem;
            font-size: 0.85rem; margin-top: 4rem; }}
            
        @media (max-width: 768px) {{
            header h1 {{ font-size: 2rem; }}
            .container {{ padding: 2rem 1rem; }}
            h2 {{ font-size: 1.6rem; }}
        }}
    </style>
</head>
<body>

    <header>
        <div class="badge">📂 Complete Project Brief & File Catalogue</div>
        <h1>Philip Harrison — Lanzarote Property Repatriation</h1>
        <p class="subtitle">A plain-English guide to everything we've done, why we've done it, and where every file lives.</p>
    </header>

    <div class="container">
        {html_content}
    </div>

    <footer>
        <p>Prepared by Dean Harrison &bull; Project Documentation & File Catalogue</p>
    </footer>

</body>
</html>"""

    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"Successfully generated HTML at {HTML_OUT}")

if __name__ == "__main__":
    convert_md_to_html()
