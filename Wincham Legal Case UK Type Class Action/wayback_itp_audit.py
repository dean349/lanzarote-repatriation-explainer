"""
WINCHAM ITP / TRANSFER TAX FORENSIC AUDIT
Searches all Wincham domains for any pages mentioning property transfer tax,
ITP, purchase tax savings, and related claims. Saves full page text and flags
specific percentage figures mentioned.
"""

import requests
import json
import os
import time
import re
from datetime import datetime
from urllib.parse import quote

# ── Evidence Output Directory ──────────────────────────────────────────────
BASE_DIR = r"c:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action\wayback_evidence"
ITP_DIR = os.path.join(BASE_DIR, "itp_evidence")
os.makedirs(ITP_DIR, exist_ok=True)

# ── All Wincham Domains ────────────────────────────────────────────────────
DOMAINS = [
    "wincham.com",
    "winchamiht.com",
    "winchamukcompany.com",
    "winchamaccountants.com",
    "winchampropertyshop.com",
]

# ── ITP-Specific Forensic Keywords ────────────────────────────────────────
ITP_KEYWORDS = [
    "transfer tax", "itp", "impuesto de transmisiones",
    "purchase tax", "property purchase tax", "stamp duty",
    "7%", "8%", "9%", "10%", "11%", "12%", "13%", "16%", "16.5%",
    "7 per cent", "10 per cent", "16.5 per cent",
    "avoid the tax", "avoid tax", "no tax", "tax free", "tax saving",
    "save on purchase", "purchase costs", "buying costs",
    "conveyancing", "resale tax", "avoid paying",
    "transfer of ownership", "property costs",
]

PERCENT_PATTERN = re.compile(r'\b(\d{1,2}(?:\.\d)?)\s*(?:%|per\s*cent)\b', re.IGNORECASE)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

log_lines = []

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    log_lines.append(line)

def safe_filename(s):
    return re.sub(r'[^\w\-_]', '_', s)[:80]

def cdx_search_itp(domain):
    """Search CDX API for pages that may contain ITP-related content."""
    log(f"\n{'='*60}")
    log(f"SEARCHING: {domain}")
    log(f"{'='*60}")

    # Search for specific ITP-related URL patterns
    itp_url_patterns = [
        f"http://*.{domain}/",
        f"http://*.{domain}/*itp*",
        f"http://*.{domain}/*purchase*",
        f"http://*.{domain}/*transfer*",
        f"http://*.{domain}/*tax*",
        f"http://*.{domain}/*stamp*",
        f"http://*.{domain}/*saving*",
        f"http://*.{domain}/*cost*",
        f"http://*.{domain}/*buy*",
        f"http://*.{domain}/*reason*",
        f"http://*.{domain}/*benefit*",
        f"http://*.{domain}/*service*",
        f"http://*.{domain}/*iht*",
        f"http://*.{domain}/*overview*",
        f"http://*.{domain}/*faq*",
        f"http://*.{domain}/*info*",
    ]

    all_snapshots = []
    seen_urls = set()

    for pattern in itp_url_patterns:
        try:
            cdx_url = (
                f"https://web.archive.org/cdx/search/cdx"
                f"?url={quote(pattern)}"
                f"&output=json"
                f"&limit=200"
                f"&fl=timestamp,original,statuscode,mimetype"
                f"&filter=statuscode:200"
                f"&filter=mimetype:text/html"
                f"&collapse=urlkey"
            )
            resp = SESSION.get(cdx_url, timeout=20)
            if resp.status_code == 200:
                rows = resp.json()
                if len(rows) > 1:
                    for row in rows[1:]:
                        ts, url, sc, mt = row
                        if url not in seen_urls:
                            seen_urls.add(url)
                            all_snapshots.append({"timestamp": ts, "url": url})
                time.sleep(0.3)
        except Exception as e:
            log(f"  CDX error for {pattern}: {e}")

    log(f"  Total unique URLs found: {len(all_snapshots)}")
    return all_snapshots


def fetch_and_analyse(snapshot, domain_dir):
    """Fetch a Wayback snapshot and check for ITP content."""
    ts = snapshot["timestamp"]
    url = snapshot["url"]
    wayback_url = f"https://web.archive.org/web/{ts}/{url}"

    try:
        resp = SESSION.get(wayback_url, timeout=25)
        if resp.status_code != 200:
            return None

        text = resp.text.lower()

        # Check for ITP keyword hits
        hits = []
        for kw in ITP_KEYWORDS:
            if kw.lower() in text:
                hits.append(kw)

        if not hits:
            return None

        # Find all percentage figures mentioned
        raw_text = resp.text
        percentages_found = PERCENT_PATTERN.findall(raw_text)
        unique_pcts = sorted(set(float(p) for p in percentages_found))
        notable_pcts = [p for p in unique_pcts if 5 <= p <= 20]

        # Extract relevant context snippets around keyword hits
        snippets = []
        raw_lower = raw_text.lower()
        for kw in hits[:5]:  # top 5 keyword matches
            idx = raw_lower.find(kw.lower())
            if idx >= 0:
                start = max(0, idx - 150)
                end = min(len(raw_text), idx + 300)
                snippet = raw_text[start:end].replace('\n', ' ').replace('\r', ' ')
                snippet = re.sub(r'\s+', ' ', snippet).strip()
                snippets.append(f"[...{snippet}...]")

        # Build result record
        result = {
            "timestamp": ts,
            "date": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}",
            "url": url,
            "wayback_url": wayback_url,
            "itp_keywords_found": hits,
            "percentages_found": notable_pcts,
            "has_high_rate": any(p >= 10 for p in notable_pcts),
            "has_16_percent": any(14 <= p <= 17 for p in notable_pcts),
            "snippets": snippets,
        }

        # Save full page text
        fn = safe_filename(f"{ts}_{url.replace('http://','').replace('https://','').replace('/','_')}")
        txt_path = os.path.join(domain_dir, f"{fn}.txt")
        with open(txt_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(f"URL: {wayback_url}\n")
            f.write(f"Date: {result['date']}\n")
            f.write(f"ITP Keywords: {', '.join(hits)}\n")
            f.write(f"Percentages found: {notable_pcts}\n")
            f.write(f"Has 16%+ figure: {result['has_high_rate']}\n")
            f.write(f"{'='*60}\n\n")
            # Strip HTML tags for cleaner text
            clean = re.sub(r'<[^>]+>', ' ', resp.text)
            clean = re.sub(r'\s+', ' ', clean)
            f.write(clean[:15000])

        return result

    except Exception as e:
        return None


def audit_domain_for_itp(domain):
    """Full ITP audit for one domain."""
    domain_key = domain.replace(".", "_")
    domain_dir = os.path.join(ITP_DIR, domain_key)
    os.makedirs(domain_dir, exist_ok=True)

    snapshots = cdx_search_itp(domain)

    results = []
    for i, snap in enumerate(snapshots):
        if i % 10 == 0:
            log(f"  Fetching {i+1}/{len(snapshots)}: {snap['url'][:60]}...")
        result = fetch_and_analyse(snap, domain_dir)
        if result:
            results.append(result)
            kw_str = ', '.join(result['itp_keywords_found'][:3])
            pct_str = str(result['percentages_found']) if result['percentages_found'] else 'none'
            flag = " ⚠️ HIGH RATE FOUND" if result['has_high_rate'] else ""
            flag16 = " 🚨 16%+ FOUND" if result['has_16_percent'] else ""
            log(f"    ✅ HIT [{result['date']}] {result['url'][:50]} | kw: {kw_str} | pct: {pct_str}{flag}{flag16}")
        time.sleep(0.8)

    return results


# ── MAIN ──────────────────────────────────────────────────────────────────
all_results = {}
summary_lines = []

for domain in DOMAINS:
    results = audit_domain_for_itp(domain)
    all_results[domain] = results
    log(f"\n  ✅ {domain}: {len(results)} ITP-related pages found")

# ── GENERATE REPORT ───────────────────────────────────────────────────────
report_path = os.path.join(ITP_DIR, "ITP_FORENSIC_FINDINGS.txt")
high_rate_path = os.path.join(ITP_DIR, "ITP_HIGH_RATE_PAGES.txt")
sixteen_pct_path = os.path.join(ITP_DIR, "ITP_16PERCENT_PAGES.txt")

high_rate_pages = []
sixteen_pct_pages = []

with open(report_path, "w", encoding="utf-8") as f:
    f.write("WINCHAM ITP / PROPERTY TRANSFER TAX — FORENSIC EVIDENCE REPORT\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*70 + "\n\n")

    for domain, results in all_results.items():
        f.write(f"\n{'='*60}\n")
        f.write(f"DOMAIN: {domain}\n")
        f.write(f"Total ITP-related pages found: {len(results)}\n")
        f.write(f"{'='*60}\n\n")

        for r in sorted(results, key=lambda x: x['date']):
            f.write(f"  Date:     {r['date']}\n")
            f.write(f"  URL:      {r['url']}\n")
            f.write(f"  Archive:  {r['wayback_url']}\n")
            f.write(f"  Keywords: {', '.join(r['itp_keywords_found'])}\n")
            f.write(f"  % Figures: {r['percentages_found']}\n")
            if r['has_high_rate']:
                f.write(f"  ⚠️  HIGH RATE (10%+) MENTIONED\n")
                high_rate_pages.append(r)
            if r['has_16_percent']:
                f.write(f"  🚨 16-17% RANGE MENTIONED\n")
                sixteen_pct_pages.append(r)
            if r['snippets']:
                f.write(f"  Context snippets:\n")
                for s in r['snippets'][:2]:
                    f.write(f"    > {s[:300]}\n")
            f.write("\n")

# Write high-rate specific report
with open(high_rate_path, "w", encoding="utf-8") as f:
    f.write("WINCHAM — PAGES MENTIONING HIGH ITP RATES (10%+)\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*70 + "\n\n")
    for r in sorted(high_rate_pages, key=lambda x: x['date']):
        f.write(f"Date: {r['date']} | Domain: {r['url'].split('/')[2]}\n")
        f.write(f"URL: {r['wayback_url']}\n")
        f.write(f"% figures seen: {r['percentages_found']}\n")
        f.write(f"Keywords: {', '.join(r['itp_keywords_found'][:5])}\n")
        for s in r['snippets'][:2]:
            f.write(f"  > {s[:400]}\n")
        f.write("\n")

# Write 16% specific report
with open(sixteen_pct_path, "w", encoding="utf-8") as f:
    f.write("WINCHAM — PAGES WHERE 14-17% RANGE WAS MENTIONED\n")
    f.write("THIS IS THE SMOKING GUN EVIDENCE FILE\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("="*70 + "\n\n")
    if sixteen_pct_pages:
        for r in sorted(sixteen_pct_pages, key=lambda x: x['date']):
            f.write(f"Date: {r['date']} | Domain: {r['url'].split('/')[2]}\n")
            f.write(f"ARCHIVED URL: {r['wayback_url']}\n")
            f.write(f"% figures present: {r['percentages_found']}\n")
            f.write(f"Keywords: {', '.join(r['itp_keywords_found'])}\n")
            for s in r['snippets']:
                f.write(f"  CONTEXT: {s[:600]}\n")
            f.write("\n")
    else:
        f.write("No pages found with 14-17% figures in relation to ITP keywords.\n")
        f.write("The 16.5% claim may have been verbal only, or appeared in non-archived materials.\n")

# Save log
log_path = os.path.join(ITP_DIR, "audit_log.txt")
with open(log_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

# Print summary
log("\n" + "="*60)
log("FORENSIC ITP AUDIT COMPLETE")
log("="*60)
for domain, results in all_results.items():
    hr = sum(1 for r in results if r['has_high_rate'])
    s16 = sum(1 for r in results if r['has_16_percent'])
    log(f"  {domain}: {len(results)} ITP pages | {hr} with 10%+ rate | {s16} with 16%+ figure")
log(f"\nMain report:       {report_path}")
log(f"High rate report:  {high_rate_path}")
log(f"16% report:        {sixteen_pct_path}")
log(f"Log:               {log_path}")
