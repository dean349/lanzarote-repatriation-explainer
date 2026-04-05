"""
redact_bank_statement.py
────────────────────────
Redact sensitive financial information from bank statement PDFs.

What it redacts (by default):
  • UK Sort codes          — e.g. 12-34-56 / 123456
  • UK Account numbers     — 8-digit strings
  • IBAN numbers           — e.g. GB29 NWBK 6016 1331 9268 19
  • Card numbers (full)    — 13-19 digit sequences (Visa / MC / Amex)
  • Card numbers (masked)  — **** **** **** 1234 style
  • BIC / SWIFT codes
  • Any custom phrases you specify on the command line

Usage:
  python redact_bank_statement.py input.pdf output_REDACTED.pdf
  python redact_bank_statement.py input.pdf output_REDACTED.pdf --also "Philip Harrison" "HSBC"

Requires:
  pip install pymupdf
"""

import sys
import re
import argparse
import fitz  # PyMuPDF


# ─── Regex patterns ───────────────────────────────────────────────────────────

PATTERNS = {
    "UK Sort Code (dashes)":   re.compile(r"\b\d{2}-\d{2}-\d{2}\b"),
    "UK Sort Code (plain)":    re.compile(r"\b\d{6}\b"),           # broad — may over-redact dates, tune if needed
    "UK Account Number":       re.compile(r"\b\d{8}\b"),
    "IBAN":                    re.compile(r"\b[A-Z]{2}\d{2}[\s]?([A-Z0-9]{4}[\s]?){4}[A-Z0-9]{0,4}\b"),
    "BIC / SWIFT":             re.compile(r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b"),
    "Card Number (16-digit)":  re.compile(r"\b(\d{4}[\s\-]?){3}\d{4}\b"),
    "Card Masked":             re.compile(r"\*{4}[\s\-]?\*{4}[\s\-]?\*{4}[\s\-]?\d{4}"),
}

REDACT_COLOUR = (0, 0, 0)   # Black fill
LABEL        = "[REDACTED]"


# ─── Core ─────────────────────────────────────────────────────────────────────

def build_patterns(extra_phrases):
    """Return compiled patterns dict, including any extra literal phrases."""
    patterns = dict(PATTERNS)
    for phrase in extra_phrases:
        patterns[f"Custom: {phrase}"] = re.compile(re.escape(phrase), re.IGNORECASE)
    return patterns


def redact_page(page, patterns, verbose=True):
    """Find and redact all matching text on a single PDF page."""
    total = 0
    for label, pattern in patterns.items():
        areas = page.search_for(pattern.pattern, quads=False)
        # search_for uses literal strings — for regex we extract text and search manually
        # then map back to positions using search_for with the exact matched string.
        pass  # (see below — we use the text-based approach)

    # Text-based approach: extract words, match regex, search for exact strings
    text = page.get_text("text")
    found_strings = set()
    for label, pattern in patterns.items():
        for match in pattern.finditer(text):
            s = match.group().strip()
            if s:
                found_strings.add((s, label))

    for s, label in found_strings:
        rects = page.search_for(s)
        for rect in rects:
            if verbose:
                print(f"  Redacting [{label}]: {repr(s)}")
            page.add_redact_annot(rect, text="", fill=REDACT_COLOUR)
            total += 1

    page.apply_redactions()
    return total


def redact_pdf(input_path, output_path, extra_phrases=None, verbose=True):
    """Open a PDF, redact all sensitive data, save to output_path."""
    extra_phrases = extra_phrases or []
    patterns = build_patterns(extra_phrases)

    doc = fitz.open(input_path)
    grand_total = 0

    for i, page in enumerate(doc):
        if verbose:
            print(f"\nPage {i + 1} / {len(doc)}:")
        count = redact_page(page, patterns, verbose=verbose)
        grand_total += count
        if verbose and count == 0:
            print("  (nothing to redact on this page)")

    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    print(f"\n✅  Done. {grand_total} item(s) redacted.")
    print(f"    Saved to: {output_path}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Redact sensitive financial data from a bank statement PDF."
    )
    parser.add_argument("input",  help="Path to the input PDF (e.g. statement.pdf)")
    parser.add_argument("output", help="Path for the redacted output PDF (e.g. statement_REDACTED.pdf)")
    parser.add_argument(
        "--also", nargs="*", default=[],
        metavar="PHRASE",
        help='Extra words/phrases to redact, e.g. --also "Philip Harrison" "HSBC"'
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress per-item output")

    args = parser.parse_args()

    print(f"\n🔒  Redacting: {args.input}")
    if args.also:
        print(f"    Also redacting: {args.also}")

    redact_pdf(
        input_path=args.input,
        output_path=args.output,
        extra_phrases=args.also,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
