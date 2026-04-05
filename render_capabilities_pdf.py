import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def html_to_pdf(playwright, html_path: Path, pdf_path: Path):
    browser = await playwright.chromium.launch()
    page = await browser.new_page()

    # Load local file — use file:/// URI
    file_uri = html_path.as_uri()
    await page.goto(file_uri, wait_until="networkidle", timeout=60000)

    # Wait for Google Fonts to load
    await page.wait_for_timeout(3000)

    await page.pdf(
        path=str(pdf_path),
        format="A4",
        margin={
            "top":    "15mm",
            "bottom": "15mm",
            "left":   "12mm",
            "right":  "12mm",
        },
        print_background=True,   # Honour background colours/gradients
    )

    await browser.close()
    size_kb = pdf_path.stat().st_size // 1024
    print(f"Generated PDF: {pdf_path.name}  ({size_kb} KB)")

async def main():
    base_dir = Path(r"c:\DAD\UK_Lanzarote_Repatriation")
    html_path = base_dir / "index.html"
    pdf_path = base_dir / "Antigravity_Capabilities.pdf"
    
    async with async_playwright() as p:
        await html_to_pdf(p, html_path, pdf_path)

if __name__ == "__main__":
    asyncio.run(main())
