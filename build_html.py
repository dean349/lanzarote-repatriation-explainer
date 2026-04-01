import markdown

with open('c:/DAD/UK_Lanzarote_Repatriation/divorce_financial_report.md', 'r', encoding='utf-8') as f:
    text = f.read()

html = markdown.markdown(text, extensions=['extra', 'tables', 'md_in_html'])

template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Philip Harrison - Financial & Divorce Settlement Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #f5f5f7;
        }}
        .container {{
            background: #ffffff;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 2rem auto;
            border-radius: 8px;
        }}
        h1, h2, h3 {{
            color: #1a202c;
            margin-top: 2rem;
        }}
        h1 {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
            margin-top: 0;
            font-size: 2.25rem;
        }}
        h2 {{
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }}
        blockquote {{
            border-left: 4px solid #4299e1;
            margin: 1.5rem 0;
            padding: 1rem 1.5rem;
            background-color: #ebf8ff;
            border-radius: 0 8px 8px 0;
            color: #2b6cb0;
        }}
        ul, ol {{
            margin-bottom: 1.5rem;
            padding-left: 1.5rem;
        }}
        li {{
            margin-bottom: 0.5rem;
        }}
        strong {{
            color: #2d3748;
        }}
        hr {{
            border: 0;
            border-top: 1px solid #e2e8f0;
            margin: 2rem 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html}
    </div>
</body>
</html>"""

with open('c:/DAD/UK_Lanzarote_Repatriation/index.html', 'w', encoding='utf-8') as f:
    f.write(template)
