"""
Update wincham-glo-opportunity/index.html on GitHub with accurate forensic figures.
Uses the GitHub REST API directly — no token limit issues.
"""
import urllib.request
import urllib.parse
import json
import base64
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dean349"
REPO  = "wincham-glo-opportunity"
PATH  = "index.html"
API   = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"

# ── 1. Fetch current file ────────────────────────────────────────────────────
req = urllib.request.Request(API, headers={
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "python-updater"
})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())

sha     = data["sha"]
content = base64.b64decode(data["content"]).decode("utf-8")

print(f"Fetched {len(content):,} bytes  SHA={sha}")

# ── 2. Targeted replacements ─────────────────────────────────────────────────
replacements = [
    # ── Page title
    ("Wincham GLO — The £10M+ UK Claims Opportunity",
     "Wincham GLO — The £97M+ UK Claims Opportunity"),

    # ── Meta description
    ("A Group Litigation Order opportunity against the Wincham International offshore scheme. 399+ identified victims, £10M+ claims pool. Commercial brief for CMC partnership and FCA authorisation.",
     "A Group Litigation Order opportunity against the Wincham International offshore scheme. 1,564+ identified victims across 782 companies, £97M+ total claims pool. Commercial brief for CMC partnership and FCA authorisation."),

    # ── Hero subtitle paragraph
    ("A forensically verified £10M+ claims pool against Wincham International Limited — 399 identified victims of an offshore property wrapper scheme that failed. We hold the only comprehensive victim database. Here's how we monetise it.",
     "A forensically verified £97M+ claims pool against Wincham International Limited — 1,564 identified victims across 782 confirmed companies. Thousands of innocent British retired couples, bled dry of their savings by Wincham's mis-sold offshore property scheme. We hold the only comprehensive victim database. Here's how we monetise it."),

    # ── Hero stat 1: victim count
    ('<span class="val">399+</span>\n        <span class="lbl">Identified Victims</span>',
     '<span class="val">1,564+</span>\n        <span class="lbl">Identified Victims</span>'),

    # ── Hero stat 2: avg loss
    ('<span class="val">£26K</span>\n        <span class="lbl">Avg. Loss Each</span>',
     '<span class="val">£120K</span>\n        <span class="lbl">Avg. Loss Each</span>'),

    # ── Hero stat 3: total pool
    ('<span class="val">£10M+</span>\n        <span class="lbl">Total Claims Pool</span>',
     '<span class="val">£97M+</span>\n        <span class="lbl">Total Claims Pool</span>'),

    # ── Metric card 1: value & label
    ('<div class="mc-val">399+</div>\n      <div class="mc-label">Victim Companies</div>\n      <div class="mc-desc">Identified from Companies House, AEAT filings and Spanish land registry — all publicly available, lawfully compiled. No other party has this database.</div>',
     '<div class="mc-val">1,564+</div>\n      <div class="mc-label">Victim Households</div>\n      <div class="mc-desc">782 confirmed companies = ~1,564 individual directors (British retired couples). Identified from Companies House, HMRC data, and AEAT filings. No other party holds this database.</div>'),

    # ── Metric card 3: CMC revenue & desc
    ('<div class="mc-val">£4M+</div>\n      <div class="mc-label">CMC Revenue Potential</div>\n      <div class="mc-desc">At 20–40% of the £10M+ claims pool, the gross CMC revenue opportunity is £2M–£4M over the life of the litigation. Phase 2 captures this in full.</div>',
     '<div class="mc-val">£24M+</div>\n      <div class="mc-label">CMC Revenue Potential</div>\n      <div class="mc-desc">At 25–40% of the £97M maximum claims pool, gross CMC revenue is £24M–£39M over the GLO lifecycle. Phase 2 captures this in full — £0 to a third-party firm.</div>'),

    # ── Section lead (opportunity section) - update £10M+ reference
    ("Wincham International Limited operated an offshore company wrapper scheme — sold to UK non-resident property vendors in Spain as a tax-saving structure. The scheme was mis-sold, the advice was unauthorised, and Brexit made it catastrophically fail. Victims are entitled to recover their losses. We hold the map to every single one of them.",
     "Wincham International Limited sold an offshore company wrapper scheme to thousands of British retired couples buying property in Spain — marketed as a legitimate tax-saving structure. The advice was negligent, unauthorised, and Brexit made it catastrophically fail. Victims are entitled to recover losses averaging £108,000–£170,000 each. The total claims pool tops £97 million. We hold the map to every single one of them."),

    # ── Phase 2 revenue figure
    ('<div class="rev-fig">£2M–£4M</div>\n        <div class="rev-note">Estimated gross CMC revenue over the full GLO lifecycle. Dean captures 65–70% of net distributable income via the marketing subcontract structure.</div>',
     '<div class="rev-fig">£24M–£39M</div>\n        <div class="rev-note">Estimated gross CMC revenue over the full GLO lifecycle at 25–40% DBA. Dean captures 65–70% of net distributable income via the marketing subcontract structure.</div>'),

    # ── JS counter: 399 → 1564
    ("if (text.includes('399')) animateCount(v, 399, '', '+');",
     "if (text.includes('1,564') || text.includes('1564')) animateCount(v, 1564, '', '+');"),

    # ── JS counter: £26K → £120K
    ("else if (text.includes('26')) animateCount(v, 26, '£', 'K');",
     "else if (text.includes('120')) animateCount(v, 120, '£', 'K');"),

    # ── JS counter: £10M → £97M
    ("else if (text.includes('10')) animateCount(v, 10, '£', 'M+');",
     "else if (text.includes('97')) animateCount(v, 97, '£', 'M+');"),
]

original = content
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"  ✓ Replaced: {old[:60].strip()!r}")
    else:
        print(f"  ✗ NOT FOUND: {old[:60].strip()!r}")

if content == original:
    print("\nNo changes made — aborting.")
    exit(1)

# ── 3. Push updated file ─────────────────────────────────────────────────────
payload = json.dumps({
    "message": "fix: update all figures to forensically verified data (April 2026)\n\n- Victims: 399+ → 1,564+ across 782 confirmed companies\n- Avg loss: £26K → £120K per victim household\n- Total pool: £10M+ → £97M+ (inc. s.455 maximum TAM)\n- CMC revenue: £4M → £24M–£39M gross\n- Updated hero narrative: British retired couples",
    "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    "sha": sha,
    "branch": "main"
}).encode("utf-8")

req2 = urllib.request.Request(API, data=payload, method="PUT", headers={
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "python-updater"
})
with urllib.request.urlopen(req2) as r:
    resp = json.loads(r.read())

new_sha = resp["content"]["sha"]
print(f"\n✅  Pushed successfully!  New SHA: {new_sha}")
print(f"🌐  https://dean349.github.io/wincham-glo-opportunity/")
