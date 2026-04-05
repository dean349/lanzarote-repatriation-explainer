html_path = r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_EXTERNAL.html'
pdf_path  = r'C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\Wincham_Pitch_Report_EXTERNAL.pdf'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove Google Fonts — causes PDF renderer to hang waiting for network
content = content.replace(
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');",
    "/* System fonts only — Google Fonts removed for PDF rendering */"
)
content = content.replace(
    "font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;",
    "font-family: 'Segoe UI', Calibri, Arial, Helvetica, sans-serif;"
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("HTML updated — Google Fonts removed")

# Now generate PDF with Playwright (offline-safe)
from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch(args=['--no-sandbox', '--disable-web-security'])
    page = browser.new_page()
    page.goto(f"file:///{html_path.replace(chr(92), '/')}", wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(2000)
    page.pdf(
        path=pdf_path,
        format="A4",
        print_background=True,
        margin={"top": "15mm", "bottom": "15mm", "left": "12mm", "right": "12mm"}
    )
    browser.close()

size_kb = os.path.getsize(pdf_path) // 1024
print(f"PDF generated: {pdf_path}")
print(f"Size: {size_kb} KB")
