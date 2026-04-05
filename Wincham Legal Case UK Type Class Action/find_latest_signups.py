"""
find_latest_signups.py
======================
Queries the Companies House Advanced Search API to find the most recently
incorporated companies at Wincham's known registered-office addresses:

  CW12 4TR  — Greenfield Farm Industrial Estate (Wincham's own address)
  CW12 4AA  — Albert Chambers, Congleton (Adrem Group / company secretary)

We sort by date_of_creation descending to pinpoint the LAST time a client
signed up to the scheme.

API key: set COMPANIES_HOUSE_API_KEY env var OR hardcode below.
"""

import ssl, base64, json, time, urllib.request, urllib.error, csv, os

API_KEY  = os.environ.get("COMPANIES_HOUSE_API_KEY", "37e01bb5-04e8-4d0d-9895-9037e31e2e36")
BASE_URL = "https://api.company-information.service.gov.uk"
BASE_DIR = r"C:\DAD\UK_Lanzarote_Repatriation\Wincham Legal Case UK Type Class Action"

ADDRESSES = [
    ("CW12 4TR", "Wincham – Greenfield Farm, Congleton"),
    ("CW12 4AA", "Adrem – Albert Chambers, Congleton"),
    ("CW12 4TR", "Wincham (alt search: secretary)"),  # same postcode, different sort
]

# ── SSL (same as other scripts) ───────────────────────────────────────────────
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req:
            new_req.headers.pop("Authorization", None)
            new_req.unredirected_hdrs.pop("authorization", None)
        return new_req

opener = urllib.request.build_opener(
    NoAuthRedirectHandler(),
    urllib.request.HTTPSHandler(context=ctx)
)
urllib.request.install_opener(opener)

def auth_header():
    return "Basic " + base64.b64encode(f"{API_KEY}:".encode()).decode()

def search_by_postcode(postcode, size=100):
    """
    Use the CH Advanced Search endpoint sorted by date descending.
    https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference/search/advanced-company-search
    """
    url = (f"{BASE_URL}/advanced-search/companies"
           f"?registered_office_address={postcode.replace(' ', '+')}"
           f"&size={size}"
           f"&start_index=0")
    
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth_header())
    req.add_header("Accept", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
        return {}
    except Exception as e:
        print(f"  Error: {e}")
        return {}

def get_officer_list(company_number):
    """Fetch directors for a company."""
    cn  = str(company_number).strip().zfill(8)
    url = f"{BASE_URL}/company/{cn}/officers"
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth_header())
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            directors = []
            for item in data.get("items", []):
                if item.get("officer_role") == "director" and not item.get("resigned_on"):
                    addr = item.get("address", {})
                    directors.append({
                        "name": item.get("name", ""),
                        "address": f"{addr.get('address_line_1','')}, {addr.get('locality','')}, {addr.get('postal_code','')}".strip(", ")
                    })
            return directors
    except Exception:
        return []

# ── Main ──────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("  WINCHAM SCHEME — MOST RECENT CLIENT SIGN-UPS")
print("  Querying Companies House Advanced Search API")
print("="*70)

all_results = []

for postcode, label in [("CW12 4TR", "Wincham – Greenfield Farm"), ("CW12 4AA", "Adrem – Albert Chambers")]:
    print(f"\n▶ Searching: {label} ({postcode}) …")
    data = search_by_postcode(postcode, size=100)
    
    items = data.get("items", [])
    total = data.get("hits", data.get("total_results", len(items)))
    print(f"  API returned {len(items)} items  (total matches: {total})")
    
    if not items:
        # Try alternative field name
        print("  Trying 'location' parameter …")
        url2 = (f"{BASE_URL}/advanced-search/companies"
                f"?location={postcode.replace(' ', '+')}"
                f"&size=100&start_index=0")
        req2 = urllib.request.Request(url2)
        req2.add_header("Authorization", auth_header())
        req2.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req2, timeout=15) as r:
                data2 = json.loads(r.read().decode())
                items = data2.get("items", [])
                total = data2.get("hits", data2.get("total_results", len(items)))
                print(f"  'location' param: {len(items)} items (total: {total})")
        except Exception as e2:
            print(f"  Also failed: {e2}")
    
    for item in items:
        all_results.append({
            "cohort":          label,
            "postcode":        postcode,
            "company_name":    item.get("company_name", ""),
            "company_number":  item.get("company_number", ""),
            "status":          item.get("company_status", ""),
            "date_created":    item.get("date_of_creation", ""),
            "company_type":    item.get("company_type", ""),
            "sic_codes":       " | ".join(item.get("sic_codes", [])),
            "registered_office": str(item.get("registered_office_address", {})),
        })
    
    time.sleep(0.6)

# ── Sort all results by date desc ─────────────────────────────────────────────
all_results.sort(key=lambda x: x["date_created"], reverse=True)

print("\n" + "="*70)
print("  TOP 30 MOST RECENTLY INCORPORATED (BOTH ADDRESSES COMBINED)")
print("="*70)
print(f"{'Date':<12}  {'Company Name':<45}  {'Number':<10}  {'Status':<12}  {'Cohort'}")
print("-"*110)
for r in all_results[:30]:
    print(f"{r['date_created']:<12}  {r['company_name'][:44]:<45}  {r['company_number']:<10}  {r['status']:<12}  {r['cohort']}")

# ── Save to CSV ───────────────────────────────────────────────────────────────
out_file = os.path.join(BASE_DIR, "latest_wincham_signups.csv")
with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
    fields = ["date_created","company_name","company_number","status","cohort","postcode","company_type","sic_codes","registered_office"]
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    for r in all_results:
        w.writerow(r)

print(f"\n✓ Full results saved to: {out_file}")
print(f"  Total companies retrieved: {len(all_results)}")

# ── Headline ──────────────────────────────────────────────────────────────────
if all_results:
    latest = all_results[0]
    print(f"\n📌 LAST KNOWN SIGN-UP DATE: {latest['date_created']}")
    print(f"   Company: {latest['company_name']}  ({latest['company_number']})")
    print(f"   Status:  {latest['status']}")
    print(f"   Cohort:  {latest['cohort']}")
