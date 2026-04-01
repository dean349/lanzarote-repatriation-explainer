import os
import markdown
import re

# File Paths
file1_md = r"C:\Users\Dean Harrison\.gemini\antigravity\brain\72e01af7-f8b8-4166-aebf-430f3836086f\artifacts\wincham_comprehensive_investigation.md"
file2_md = r"c:\DAD\UK_Lanzarote_Repatriation\Files and Information for Phil Harrison\MASTER_REPORT_Wincham_Adrem_Los_Romeros.md"

output1_html = r"c:\DAD\UK_Lanzarote_Repatriation\index.html"
output2_html = r"c:\DAD\UK_Lanzarote_Repatriation\historical_ledger.html"

# Common HTML Template
def build_html(title, content_html, active_page="executive"):
    # Determine Nav classes
    exec_class = 'active' if active_page == 'executive' else ''
    ledger_class = 'active' if active_page == 'ledger' else ''

    # Custom styling for GitHub style blockquotes (CAUTION/IMPORTANT/NOTE)
    content_html = content_html.replace('<blockquote>\n<p>[!CAUTION]', '<blockquote class="alert caution"><strong>🚨 CAUTION</strong><br/>')
    content_html = content_html.replace('<blockquote>\n<p>[!IMPORTANT]', '<blockquote class="alert important"><strong>⚠️ IMPORTANT</strong><br/>')
    content_html = content_html.replace('<blockquote>\n<p>[!NOTE]', '<blockquote class="alert note"><strong>💡 NOTE</strong><br/>')
    content_html = content_html.replace('<blockquote>\n<p>[!WARNING]', '<blockquote class="alert warning"><strong>⚠️ WARNING</strong><br/>')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --navy:   #1a2744;
      --navy2:  #243560;
      --gold:   #c9952a;
      --gold2:  #e8b44e;
      --white:  #ffffff;
      --lgrey:  #f5f7fa;
      --mgrey:  #6b7280;
      --dgrey:  #374151;
      --border: #e2e8f0;
      --blue-bg:#dbeafe;
      --blue-b: #3b82f6;
      --amb-bg: #fef3c7;
      --amb-b:  #d97706;
      --red-bg: #fee2e2;
      --red-b:  #dc2626;
      --purp-bg: #f3e8ff;
      --purp-b: #a855f7;
      --talt:   #f0f4fa;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: var(--lgrey);
      color: var(--dgrey);
      line-height: 1.6;
    }}

    /* ── HERO & NAVBAR ── */
    .hero {{
      background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 100%);
      color: var(--white);
      padding: 40px 16px 30px;
      text-align: center;
    }}
    .hero-badge {{
      display: inline-block;
      background: rgba(201,149,42,0.25);
      border: 1px solid var(--gold);
      color: var(--gold2);
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      padding: 4px 16px;
      border-radius: 999px;
      margin-bottom: 18px;
    }}
    .hero h1 {{
      font-family: 'Playfair Display', serif;
      font-size: clamp(1.6rem, 5vw, 3rem);
      line-height: 1.2;
      max-width: 800px;
      margin: 0 auto 14px;
    }}
    .hero p {{
      color: #94a3b8;
      font-size: 0.95rem;
      margin-bottom: 4px;
    }}
    
    /* Top Navigation inside hero (TABS) */
    .top-nav {{
      margin-top: 40px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      justify-content: center;
      max-width: 900px;
      margin-left: auto;
      margin-right: auto;
      background: rgba(0,0,0,0.25);
      border-radius: 12px;
      padding: 8px;
      border: 1px solid rgba(255,255,255,0.05);
    }}
    @media(min-width: 768px) {{
      .top-nav {{
        flex-direction: row;
        gap: 0;
      }}
    }}
    .top-nav-link {{
      flex: 1;
      background: transparent;
      color: rgba(255, 255, 255, 0.7);
      text-decoration: none;
      font-weight: 700;
      padding: 18px 20px;
      border-radius: 8px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border: none;
      text-align: center;
      font-size: 1.15rem;
      letter-spacing: 0.02em;
      position: relative;
    }}
    .top-nav-link:hover {{
      color: var(--white);
      background: rgba(255, 255, 255, 0.1);
    }}
    .top-nav-link.active {{
      background: var(--gold);
      color: var(--navy);
      box-shadow: 0 4px 20px rgba(201, 149, 42, 0.5);
    }}
    
    .hero-subtext {{
      margin-top: 18px;
      font-size: 1rem;
      color: rgba(255, 255, 255, 0.9);
      font-style: italic;
      font-weight: 500;
      max-width: 700px;
      margin-left: auto;
      margin-right: auto;
      line-height: 1.5;
    }}
    .hero-subtext strong {{
      color: var(--gold2);
      font-weight: 700;
      font-style: normal;
    }}
    
    @media(min-width: 850px) {{
      .hero {{
        padding: 60px 20px 50px;
      }}
    }}

    /* ── LAYOUT (Mobile First) ── */
    .layout {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
      max-width: 1200px;
      margin: 20px auto;
      padding: 0 16px;
      align-items: start;
    }}
    @media(min-width: 850px) {{
       .layout {{
         grid-template-columns: 280px 1fr;
         gap: 30px;
         margin: 40px auto;
         padding: 0 20px;
       }}
    }}

    /* ── SIDEBAR (TOC) ── */
    .sidebar {{
      background: var(--white);
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
      padding: 20px;
      max-height: 350px;
      overflow-y: auto;
    }}
    @media(min-width: 850px) {{
      .sidebar {{
        position: sticky;
        top: 20px;
        padding: 24px;
        max-height: calc(100vh - 40px);
      }}
    }}
    .sidebar h3 {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--navy);
      margin-bottom: 16px;
      border-bottom: 2px solid var(--border);
      padding-bottom: 8px;
    }}
    .toc-link {{
      display: block;
      font-size: 0.88rem;
      color: var(--mgrey);
      text-decoration: none;
      margin-bottom: 10px;
      line-height: 1.4;
      padding-left: 12px;
      border-left: 2px solid transparent;
      transition: all 0.2s ease;
    }}
    .toc-link:hover {{
      color: var(--navy);
      border-left-color: var(--gold);
    }}
    .toc-link.active {{
      color: var(--navy);
      font-weight: 600;
      border-left-color: var(--gold);
      background: var(--lgrey);
      padding-top: 4px;
      padding-bottom: 4px;
      border-radius: 0 4px 4px 0;
    }}

    .toc-link.h2 {{ font-weight: 600; font-size: 0.92rem; color: var(--navy); margin-top: 14px; padding-left: 0; border-left: none; }}
    .toc-link.h3 {{ padding-left: 14px; font-size: 0.85rem; }}

    /* ── CONTENT AREA ── */
    .content {{
      background: var(--white);
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
      padding: 24px 20px;
      overflow-x: hidden;
    }}
    @media(min-width: 850px) {{
      .content {{ padding: 40px 50px; }}
    }}

    /* ── TYPOGRAPHY IN CONTENT ── */
    .content h1 {{
      font-family: 'Playfair Display', serif;
      font-size: clamp(1.8rem, 4vw, 2.4rem);
      color: var(--navy);
      margin-bottom: 20px;
      line-height: 1.2;
    }}
    .content h2 {{
      font-size: clamp(1.3rem, 4vw, 1.5rem);
      color: var(--navy);
      margin: 40px 0 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid var(--border);
    }}
    .content h2:first-child {{ margin-top: 0; }}
    
    .content h3 {{
      font-size: clamp(1.05rem, 3vw, 1.1rem);
      color: var(--navy);
      margin: 28px 0 12px;
    }}
    
    .content h4 {{
      font-size: 0.95rem;
      color: var(--gold);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 24px 0 10px;
    }}
    
    .content p {{ margin-bottom: 16px; font-size: 1.05rem; font-weight: 500; color: #111827; }}
    .content ul, .content ol {{ margin-bottom: 16px; padding-left: 24px; font-size: 1.05rem; font-weight: 500; color: #111827; }}
    .content li {{ margin-bottom: 6px; }}
    .content strong {{ color: var(--navy); font-weight: 600; }}
    .content a {{ color: var(--blue-b); text-decoration: none; word-wrap: break-word; }}
    .content a:hover {{ text-decoration: underline; }}

    /* ── TABLES ── */
    .table-wrapper {{
      width: 100%;
      overflow-x: auto;
      margin-bottom: 2em;
      border-radius: 8px;
    }}
    .content table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 0.9rem;
      min-width: 500px;
    }}
    .content th {{
      background: var(--navy);
      color: var(--white);
      padding: 12px 16px;
      text-align: left;
      font-weight: 600;
    }}
    .content td {{
      padding: 10px 16px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    .content tr:nth-child(even) td {{ background: var(--talt); }}

    /* ── ALERT BOXES ── */
    blockquote {{
      background: var(--surface);
      border-left: 4px solid var(--muted);
      padding: 16px 20px;
      border-radius: 0 var(--radius) var(--radius) 0;
      margin-bottom: 1.5em;
      font-style: italic;
      color: #c7d6ef;
      word-wrap: break-word;
    }}
    .alert {{
      border-left: 4px solid;
      border-radius: 0 8px 8px 0;
      padding: 16px 20px;
      margin: 24px 0;
      font-size: 0.95rem;
      line-height: 1.6;
      font-style: normal;
    }}
    .alert p:last-child {{ margin-bottom: 0; }}
    .alert.info     {{ background: var(--blue-bg); border-color: var(--blue-b); color: #1e40af; }}
    .alert.warning  {{ background: var(--amb-bg);  border-color: var(--amb-b);  color: #92400e; }}
    .alert.important{{ background: var(--purp-bg); border-color: var(--purp-b); color: #6b21a8; }}
    .alert.caution  {{ background: var(--red-bg);  border-color: var(--red-b);  color: #991b1b; }}
    .alert.note     {{ background: var(--blue-bg); border-color: var(--blue-b); color: #1e40af; }}
    .alert strong {{
      display: block;
      margin-bottom: 6px;
      text-transform: uppercase;
      font-size: 0.8rem;
      letter-spacing: 0.06em;
    }}

    code {{ background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.85em; word-wrap: break-word; color: var(--navy); }}
    
    /* ── FOOTER ── */
    footer {{
      text-align: center;
      padding: 30px 20px 50px;
      color: var(--mgrey);
      font-size: 0.85rem;
      line-height: 1.7;
    }}
    
    hr {{
      border: 0; margin: 40px 0;
      border-top: 1px solid var(--border);
    }}
    
  </style>
</head>
<body>

  <div class="hero">
    <div class="hero-badge">Confidential — Private & Family Reference</div>
    <h1>FORENSIC REPORTING PORTAL</h1>
    <p>Philip Harrison &mdash; Lanzarote Property Sale</p>
    
    <nav class="top-nav">
      <a href="index.html" class="top-nav-link {exec_class}">Action Plan & Executive Briefing</a>
      <a href="historical_ledger.html" class="top-nav-link {ledger_class}">17-Year Historical Ledger & Evidence Vault</a>
    </nav>
    <p class="hero-subtext">&#8594; <strong>Start here:</strong> Read the Action Plan & Executive Briefing first, then switch to the 17-Year Historical Ledger & Evidence Vault for the complete timeline.</p>
  </div>

  <div class="layout">
    <aside class="sidebar">
      <h3>Contents</h3>
      <nav id="toc-nav">
        <!-- Will be populated by JS based on headings -->
      </nav>
    </aside>
    
    <main class="content" id="report-content">
      {content_html}
    </main>
  </div>

  <footer>
    <p>Philip Harrison &mdash; Lanzarote Property Sale &mdash; Forensic Report</p>
    <p>Prepared 29 March 2026 &bull; AI Advisory Team</p>
  </footer>

  <script>
    // Build TOC dynamically from H2 and H3 tags
    const content = document.getElementById('report-content');
    const tocNav = document.getElementById('toc-nav');
    const headings = content.querySelectorAll('h2, h3');
    
    headings.forEach(heading => {{
      // skip if no ID
      if (!heading.id) return;
      
      const link = document.createElement('a');
      link.href = '#' + heading.id;
      link.textContent = heading.textContent;
      link.className = 'toc-link ' + heading.tagName.toLowerCase();
      
      // For H2s, let's remove "PART X -" or "PHASE X -" to make it cleaner in TOC
      if (heading.tagName === 'H2') {{
          link.textContent = heading.textContent.replace(/^(PART|PHASE) \d+ [—|-] /, '');
      }}
      
      tocNav.appendChild(link);
    }});

    // Intersection Observer for highlighting TOC dynamically
    const observerOptions = {{
      root: null,
      rootMargin: '0px 0px -60% 0px',
      threshold: 0.1
    }};

    const observer = new IntersectionObserver(entries => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          const id = entry.target.id;
          document.querySelectorAll('.toc-link').forEach(link => {{
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + id) {{
              link.classList.add('active');
            }}
          }});
        }}
      }});
    }}, observerOptions);

    headings.forEach(heading => observer.observe(heading));
  </script>

</body>
</html>"""
    return html

def process_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    # Convert MD to HTML (tables extension is critical)
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])
    
    # Wrap tables for responsive horizontal scrolling
    html_content = html_content.replace('<table>', '<div class="table-wrapper"><table>')
    html_content = html_content.replace('</table>', '</table></div>')
    
    return html_content

def main():
    # Render File 1
    content1 = process_markdown(file1_md)
    html1 = build_html("Executive Briefing — Forensic Portal", content1, "executive")
    with open(output1_html, 'w', encoding='utf-8') as f:
        f.write(html1)
    
    # Render File 2
    content2 = process_markdown(file2_md)
    html2 = build_html("Historical Ledger — Forensic Portal", content2, "ledger")
    with open(output2_html, 'w', encoding='utf-8') as f:
        f.write(html2)
        
    print(f"Success! Generated:\n- {output1_html}\n- {output2_html}")

if __name__ == "__main__":
    main()
