#!/usr/bin/env python3
"""
html_to_pdf_playwright.py
Renders styled HTML files to PDF using headless Chromium via Playwright.
Produces print-quality output identical to Chrome's 'Print to PDF'.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action")

FILES = [
    "Wincham_Nine_Task_Verification_Report.html",
    "Wincham_Legitimate_Interests_Assessment.html",
    "Wincham_ICAEW_Disciplinary_Referral.html",
]

async def html_to_pdf(playwright, html_path: Path, pdf_path: Path):
    browser = await playwright.chromium.launch()
    page = await browser.new_page()

    # Load local file — use file:/// URI
    file_uri = html_path.as_uri()
    await page.goto(file_uri, wait_until="networkidle", timeout=60000)

    # Wait for Google Fonts to load (gives ~3s for font swap)
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
    print(f"  ✓  {pdf_path.name}  ({size_kb} KB)")


async def main():
    async with async_playwright() as p:
        # Install Chromium if not present
        for filename in FILES:
            html_path = BASE_DIR / filename
            pdf_path  = BASE_DIR / filename.replace(".html", ".pdf")

            if not html_path.exists():
                print(f"  ✗  MISSING: {html_path}")
                continue

            print(f"\nRendering: {filename}")
            await html_to_pdf(p, html_path, pdf_path)

    print("\nAll done.")


if __name__ == "__main__":
    asyncio.run(main())
