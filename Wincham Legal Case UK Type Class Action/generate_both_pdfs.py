"""
Generate PDFs for:
1. Ellis_Briefing_Document.pdf  (updated with Part 1A)
2. Wincham_Letter_of_Claim_Philip_Harrison.pdf  (new file)

Uses Playwright for high-fidelity rendering (fonts, gradients, colours).
Falls back to WeasyPrint if Playwright is not available.
"""
import subprocess, sys, pathlib

DIR = pathlib.Path(__file__).parent

JOBS = [
    (DIR / "Ellis_Briefing_Document.html",
     DIR / "Ellis_Briefing_Document.pdf"),
    (DIR / "Wincham_Letter_of_Claim_Philip_Harrison.html",
     DIR / "Wincham_Letter_of_Claim_Philip_Harrison.pdf"),
]

def try_playwright(html_file, pdf_file):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed — installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"])
        except Exception:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright

    from playwright.sync_api import sync_playwright
    print(f"  Rendering with Playwright → {pdf_file.name}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_file.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2500)   # let web fonts settle
        page.pdf(
            path=str(pdf_file),
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "14mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()
    print(f"  ✅  PDF saved: {pdf_file.name}")

def try_weasyprint(html_file, pdf_file):
    try:
        import weasyprint
    except ImportError:
        print("WeasyPrint not installed — installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint", "-q"])
        import weasyprint
    print(f"  Rendering with WeasyPrint → {pdf_file.name}")
    weasyprint.HTML(filename=str(html_file)).write_pdf(str(pdf_file))
    print(f"  ✅  PDF saved: {pdf_file.name}")

for html_path, pdf_path in JOBS:
    print(f"\n{'='*60}")
    print(f"Processing: {html_path.name}")
    try:
        try_playwright(html_path, pdf_path)
    except Exception as e1:
        print(f"  Playwright failed ({e1}), trying WeasyPrint...")
        try:
            try_weasyprint(html_path, pdf_path)
        except Exception as e2:
            print(f"  ❌ Both renderers failed for {html_path.name}: {e2}")

print("\n✅ All done.")
