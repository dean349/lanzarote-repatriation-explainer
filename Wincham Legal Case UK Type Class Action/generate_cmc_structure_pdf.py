"""
Generate CMC_Commercial_Structure.pdf from the HTML source.
Uses playwright for high-fidelity rendering (fonts, gradients, colours).
Falls back to weasyprint if playwright is not available.
"""
import subprocess, sys, pathlib, os

HTML_FILE = pathlib.Path(__file__).parent / "CMC_Commercial_Structure.html"
PDF_FILE  = pathlib.Path(__file__).parent / "CMC_Commercial_Structure.pdf"

def try_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed — trying to install...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"])
        except Exception:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright

    from playwright.sync_api import sync_playwright
    print(f"Rendering with Playwright → {PDF_FILE.name}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(HTML_FILE.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2000)   # let web fonts settle
        page.pdf(
            path=str(PDF_FILE),
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()
    print(f"✅  PDF saved: {PDF_FILE}")

def try_weasyprint():
    try:
        import weasyprint
    except ImportError:
        print("WeasyPrint not installed — installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint", "-q"])
        import weasyprint

    print(f"Rendering with WeasyPrint → {PDF_FILE.name}")
    weasyprint.HTML(filename=str(HTML_FILE)).write_pdf(str(PDF_FILE))
    print(f"✅  PDF saved: {PDF_FILE}")

if __name__ == "__main__":
    try:
        try_playwright()
    except Exception as e1:
        print(f"Playwright failed ({e1}), trying WeasyPrint...")
        try:
            try_weasyprint()
        except Exception as e2:
            print(f"WeasyPrint also failed ({e2})")
            sys.exit(1)
