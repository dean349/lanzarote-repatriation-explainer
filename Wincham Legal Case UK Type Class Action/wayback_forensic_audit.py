"""
Wincham Group - Wayback Machine Forensic Audit
===============================================
Queries the Internet Archive CDX API for all Wincham-related domains,
downloads key archived page content, and generates a forensic report.

Domains investigated:
  - wincham.com          (main group site)
  - winchamaccountants.com
  - winchamukcompany.com
  - winchamiht.com       (IHT / Inheritance Tax site)
  - winchampropertyshop.com
"""

import requests
import time
import json
import os
import re
from datetime import datetime
from pathlib import Path

# ── Output directory ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "wayback_evidence"
OUTPUT_DIR.mkdir(exist_ok=True)

DOMAINS = [
    "wincham.com",
    "winchamaccountants.com",
    "winchamukcompany.com",
    "winchamiht.com",
    "winchampropertyshop.com",
]

# High-value keyword patterns for forensic flagging
FORENSIC_KEYWORDS = [
    "inheritance tax", "iht", "spain", "spanish", "lanzarote", "canary",
    "uk limited company", "uk company", "corporate wrapper", "offshore",
    "tax efficient", "tax free", "avoid", "avoidance", "saving",
    "ftcr", "foreign tax", "double taxation", "mvl", "liquidation",
    "guarantee", "guaranteed", "qualified", "aat", "acca", "icaew",
    "regulated", "authorised", "fca", "hmrc approved",
    "brexit", "post brexit", "eu", "european",
    "annual return", "company secretary", "registered office",
    "no capital gains", "no cgt", "stamp duty", "sdlt",
]

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "WinchamForensicAudit/1.0 (legal research)"})


# ── CDX Snapshot listing ──────────────────────────────────────────────────────
def get_cdx_snapshots(domain: str, from_year="2008", to_year="2026") -> list:
    """Fetch all archived URLs for a domain from the CDX API."""
    url = (
        f"https://web.archive.org/cdx/search/cdx"
        f"?url={domain}/*"
        f"&output=json"
        f"&fl=timestamp,original,statuscode,mimetype"
        f"&limit=1000"
        f"&from={from_year}0101"
        f"&to={to_year}1231"
        f"&collapse=urlkey"
        f"&filter=mimetype:text/html"
        f"&filter=statuscode:200"
    )
    print(f"  Querying CDX for {domain}...")
    for attempt in range(4):
        try:
            r = SESSION.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                if len(data) <= 1:
                    return []
                headers = data[0]
                rows = [dict(zip(headers, row)) for row in data[1:]]
                print(f"    ✓ Found {len(rows)} snapshots")
                return rows
            elif r.status_code == 503:
                print(f"    ⚠ 503 rate-limited, waiting {10*(attempt+1)}s...")
                time.sleep(10 * (attempt + 1))
            else:
                print(f"    ✗ HTTP {r.status_code}")
                return []
        except Exception as e:
            print(f"    ✗ Error: {e}, retrying...")
            time.sleep(8)
    return []


# ── Fetch archived page content ───────────────────────────────────────────────
def fetch_archived_page(timestamp: str, original_url: str) -> str | None:
    """Fetch the raw text content of a specific Wayback Machine snapshot."""
    wayback_url = f"https://web.archive.org/web/{timestamp}if_/{original_url}"
    for attempt in range(3):
        try:
            r = SESSION.get(wayback_url, timeout=25, allow_redirects=True)
            if r.status_code == 200:
                return r.text
            time.sleep(3)
        except Exception as e:
            print(f"      ✗ fetch error: {e}")
            time.sleep(5)
    return None


def extract_text(html: str) -> str:
    """Crude but dependency-free text extraction from HTML."""
    # Remove scripts and styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def flag_keywords(text: str) -> list:
    """Return list of forensic keywords found in the text."""
    text_lower = text.lower()
    return [kw for kw in FORENSIC_KEYWORDS if kw in text_lower]


# ── Select representative snapshots per domain ────────────────────────────────
def select_key_snapshots(snapshots: list) -> list:
    """
    Pick ~1 snapshot per year, prioritising homepage and key service pages.
    Returns a deduplicated list of (timestamp, original_url) tuples.
    """
    # Prioritise homepage and service pages
    priority_patterns = [
        r'^https?://(?:www\.)?[^/]+/?$',           # homepage
        r'/services?', r'/tax', r'/spain', r'/spanish',
        r'/iht', r'/inheritance', r'/company', r'/about',
        r'/lanzarote', r'/canary', r'/overseas', r'/uk-company',
        r'/how-it-works', r'/pricing', r'/fees', r'/why',
        r'/faqs?', r'/news', r'/blog',
    ]

    by_year: dict[str, list] = {}
    for snap in snapshots:
        year = snap["timestamp"][:4]
        by_year.setdefault(year, []).append(snap)

    selected = []
    for year in sorted(by_year.keys()):
        year_snaps = by_year[year]
        # Sort: homepage first, then by priority pattern rank
        def priority(s):
            url = s["original"].rstrip("/")
            for i, pat in enumerate(priority_patterns):
                if re.search(pat, url, re.IGNORECASE):
                    return i
            return 99
        year_snaps.sort(key=priority)
        # Take up to 3 per year (homepage + 2 service pages)
        seen_urls = set()
        count = 0
        for snap in year_snaps:
            url_key = snap["original"].rstrip("/").split("?")[0]
            if url_key not in seen_urls and count < 3:
                selected.append(snap)
                seen_urls.add(url_key)
                count += 1

    return selected


# ── Main audit loop ───────────────────────────────────────────────────────────
def audit_domain(domain: str) -> dict:
    print(f"\n{'='*60}")
    print(f"  AUDITING: {domain}")
    print(f"{'='*60}")

    result = {
        "domain": domain,
        "total_snapshots": 0,
        "years_active": [],
        "key_pages_audited": [],
        "forensic_flags": [],
        "timeline_summary": [],
    }

    snapshots = get_cdx_snapshots(domain)
    if not snapshots:
        print(f"  ✗ No snapshots found for {domain}")
        result["timeline_summary"].append("NO ARCHIVE DATA FOUND")
        return result

    result["total_snapshots"] = len(snapshots)
    years = sorted(set(s["timestamp"][:4] for s in snapshots))
    result["years_active"] = years
    print(f"  Years with archives: {', '.join(years)}")

    key_snaps = select_key_snapshots(snapshots)
    print(f"  Selected {len(key_snaps)} key snapshots to fetch...")

    domain_dir = OUTPUT_DIR / domain.replace(".", "_")
    domain_dir.mkdir(exist_ok=True)

    all_flags = {}   # timestamp -> list of keywords
    page_summaries = []

    for i, snap in enumerate(key_snaps):
        ts = snap["timestamp"]
        original = snap["original"]
        date_str = datetime.strptime(ts[:8], "%Y%m%d").strftime("%d %b %Y")

        print(f"  [{i+1}/{len(key_snaps)}] {date_str}: {original[:80]}")
        time.sleep(2)  # Be polite to the archive

        html = fetch_archived_page(ts, original)
        if not html:
            print(f"    ✗ Could not fetch")
            continue

        text = extract_text(html)
        found_kws = flag_keywords(text)

        # Save raw text
        safe_name = re.sub(r'[^\w]', '_', original)[:80]
        txt_path = domain_dir / f"{ts}_{safe_name}.txt"
        txt_path.write_text(text[:50000], encoding="utf-8", errors="replace")

        page_summary = {
            "timestamp": ts,
            "date": date_str,
            "url": original,
            "wayback_url": f"https://web.archive.org/web/{ts}/{original}",
            "forensic_keywords": found_kws,
            "text_preview": text[:800],
        }
        page_summaries.append(page_summary)

        if found_kws:
            print(f"    🚩 FORENSIC FLAGS: {', '.join(found_kws[:8])}")
            all_flags[ts] = found_kws
        else:
            print(f"    ✓ No forensic keywords found")

    result["key_pages_audited"] = page_summaries
    result["forensic_flags"] = all_flags

    # Generate timeline summary
    for year in years:
        year_pages = [p for p in page_summaries if p["timestamp"][:4] == year]
        year_flags = []
        for p in year_pages:
            year_flags.extend(p.get("forensic_keywords", []))
        result["timeline_summary"].append({
            "year": year,
            "pages_fetched": len(year_pages),
            "flags": list(set(year_flags)),
        })

    return result


# ── Report generator ──────────────────────────────────────────────────────────
def generate_report(all_results: list[dict]) -> str:
    lines = []
    lines.append("WINCHAM GROUP — WAYBACK MACHINE FORENSIC AUDIT REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M UTC')}")
    lines.append("=" * 70)
    lines.append("")

    for res in all_results:
        domain = res["domain"]
        lines.append(f"\n{'─'*60}")
        lines.append(f"DOMAIN: {domain}")
        lines.append(f"Total archived snapshots found: {res['total_snapshots']}")
        lines.append(f"Years active in archive:       {', '.join(res['years_active'])}")
        lines.append("")

        if not res["years_active"]:
            lines.append("  ⚠  NO WAYBACK MACHINE ARCHIVE DATA EXISTS FOR THIS DOMAIN")
            lines.append("     This may indicate: (a) the site never existed, (b) robots.txt")
            lines.append("     blocked crawling, or (c) deliberate exclusion was requested.")
            lines.append("")
            continue

        lines.append("TIMELINE:")
        for ts in res["timeline_summary"]:
            if isinstance(ts, str):
                lines.append(f"  {ts}")
                continue
            flag_str = f" | FLAGS: {', '.join(ts['flags'])}" if ts["flags"] else ""
            lines.append(f"  {ts['year']}: {ts['pages_fetched']} page(s) audited{flag_str}")

        lines.append("")
        lines.append("FORENSICALLY FLAGGED PAGES:")
        flagged = [p for p in res.get("key_pages_audited", []) if p.get("forensic_keywords")]
        if not flagged:
            lines.append("  None found in sampled pages.")
        for p in flagged:
            lines.append(f"\n  📅 {p['date']}")
            lines.append(f"  🔗 {p['wayback_url']}")
            lines.append(f"  🚩 Keywords: {', '.join(p['forensic_keywords'])}")
            lines.append(f"  📄 Preview: {p['text_preview'][:300]}...")
            lines.append("")

    lines.append("")
    lines.append("=" * 70)
    lines.append("WAYBACK MACHINE DIRECT ACCESS URLS FOR LEGAL REVIEW")
    lines.append("=" * 70)
    lines.append("")
    for res in all_results:
        lines.append(f"\nDomain: {res['domain']}")
        lines.append(f"  Calendar view: https://web.archive.org/web/*/{res['domain']}")
        for p in res.get("key_pages_audited", [])[:5]:
            lines.append(f"  • {p['date']}: {p['wayback_url']}")

    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*70)
    print("  WINCHAM GROUP — WAYBACK MACHINE FORENSIC AUDIT")
    print("="*70)
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Domains to audit: {len(DOMAINS)}")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")

    all_results = []
    for domain in DOMAINS:
        result = audit_domain(domain)
        all_results.append(result)

        # Save per-domain JSON
        json_path = OUTPUT_DIR / f"{domain.replace('.', '_')}_audit.json"
        json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"  💾 Saved: {json_path.name}")

        time.sleep(5)  # Pause between domains

    # Save full results JSON
    full_json = OUTPUT_DIR / "wincham_wayback_full_audit.json"
    full_json.write_text(json.dumps(all_results, indent=2), encoding="utf-8")

    # Generate and save report
    report = generate_report(all_results)
    report_path = OUTPUT_DIR / "wincham_wayback_forensic_report.txt"
    report_path.write_text(report, encoding="utf-8")

    print("\n" + "=" * 70)
    print("  AUDIT COMPLETE")
    print(f"  📄 Report: {report_path}")
    print(f"  📦 Full JSON: {full_json}")
    print("=" * 70)
    print()
    print(report)


if __name__ == "__main__":
    main()
