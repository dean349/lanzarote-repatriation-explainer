"""
Adrem Accounting Victim Harvester — CW12 4AA
============================================
Uses read_url approach that works: fetches each page from Companies House
Advanced Search (CW12 4AA), parses the markdown-converted content,
then calls the API for each company's directors.

Relies on the fact that read_url works for these pages.
Output: adrem_cw12_4aa_leads.csv
"""

import requests
import time
import csv
import re
import sys

API_KEY = "4416608c-08ec-449e-8c5a-ddc66b5bb6b3"
BASE_URL = "https://api.company-information.service.gov.uk"
OUTPUT_FILE = "adrem_cw12_4aa_leads.csv"

PAGES = list(range(1, 11))  # Pages 1–10

PAGE_URL_TEMPLATE = (
    "https://find-and-update.company-information.service.gov.uk/advanced-search/get-results"
    "?registeredOfficeAddress=CW12+4AA"
    "&incorporationFromDay=&incorporationFromMonth=&incorporationFromYear="
    "&incorporationToDay=&incorporationToMonth=&incorporationToYear="
    "&dissolvedFromDay=&dissolvedFromMonth=&dissolvedFromYear="
    "&dissolvedToDay=&dissolvedToMonth=&dissolvedToYear="
    "&page={page}"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}


def fetch_page_html(page_num, retries=3):
    url = PAGE_URL_TEMPLATE.format(page=page_num)
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=25)
            if resp.status_code == 200:
                return resp.text
            print(f"\n  Page {page_num} returned HTTP {resp.status_code} (attempt {attempt+1})")
        except Exception as e:
            print(f"\n  Page {page_num} error: {e} (attempt {attempt+1})")
        time.sleep(2)
    return ""


def parse_companies_from_html(html):
    """
    Extract companies from Companies House search results HTML.
    Each company block looks like:
      <h2 class="govuk-heading-m ...">
        <a href="/company/NNNNNNNN">COMPANY NAME</a>
      </h2>
      ...
      <p>Active</p>  or <p>Dissolved</p>
      <p class="govuk-body govuk-!-margin-bottom-1">
        Private limited company
      </p>
    """
    companies = []
    # Extract company number and name from href links
    # Pattern: href="/company/XXXXXXXX" then text is the company name
    pattern = re.compile(
        r'href="/company/(\d{8})(?:\?[^"]*)?"[^>]*>([^<]+)</a>',
        re.IGNORECASE
    )
    for m in pattern.finditer(html):
        num = m.group(1)
        name = m.group(2).strip()
        # Filter out navigation links etc — company names have them
        if len(name) > 3 and not name.startswith("link opens"):
            companies.append({
                "company_number": num,
                "company_name": name,
            })

    # Deduplicate preserving order
    seen = set()
    unique = []
    for c in companies:
        if c["company_number"] not in seen:
            seen.add(c["company_number"])
            unique.append(c)

    return unique


def fetch_company_detail(company_number):
    url = f"{BASE_URL}/company/{company_number}"
    try:
        resp = requests.get(url, auth=(API_KEY, ""), timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {}


def fetch_directors(company_number):
    url = f"{BASE_URL}/company/{company_number}/officers"
    try:
        resp = requests.get(url, auth=(API_KEY, ""), timeout=15)
        if resp.status_code != 200:
            return []

        directors = []
        for item in resp.json().get("items", []):
            if "director" not in item.get("officer_role", "").lower():
                continue
            if item.get("resigned_on"):
                continue  # Skip resigned

            addr = item.get("address", {})
            address_str = ", ".join(filter(None, [
                addr.get("care_of", ""),
                addr.get("premises", ""),
                addr.get("address_line_1", ""),
                addr.get("address_line_2", ""),
                addr.get("locality", ""),
                addr.get("region", ""),
                addr.get("postal_code", ""),
                addr.get("country", ""),
            ]))

            directors.append({
                "name": item.get("name", ""),
                "role": item.get("officer_role", ""),
                "address": address_str,
                "appointed_on": item.get("appointed_on", ""),
            })
        return directors
    except Exception:
        return []


def main():
    print("=" * 62)
    print("  ADREM ACCOUNTING VICTIM HARVESTER — CW12 4AA")
    print("  1-2 Albert Chambers, Canal Street, Congleton")
    print("=" * 62)

    # ── Step 1: Scrape all pages ────────────────────────────────────────────
    print(f"\n[1/3] Fetching 10 pages from Companies House...\n")
    all_companies = {}

    for page in PAGES:
        sys.stdout.write(f"  Page {page:2d}/10 — ")
        sys.stdout.flush()
        html = fetch_page_html(page)

        if not html:
            print(f"FAILED (empty response)")
            continue

        companies = parse_companies_from_html(html)
        new_this_page = 0
        for c in companies:
            if c["company_number"] not in all_companies:
                all_companies[c["company_number"]] = c
                new_this_page += 1

        print(f"+{new_this_page} new companies (running total: {len(all_companies)})")
        time.sleep(1.0)

    print(f"\n  Total unique companies: {len(all_companies)}")

    if not all_companies:
        print("\n  ERROR: No companies retrieved.")
        print("  The Companies House website may be blocking automated requests.")
        print("  Try running the browser-based approach instead.")
        return

    companies_list = list(all_companies.values())

    # ── Step 2: Fetch details + directors ──────────────────────────────────
    print(f"\n[2/3] Fetching directors for {len(companies_list)} companies via API...")
    print(f"      Using API key: {API_KEY[:12]}...")

    # Test API connectivity first
    test_resp = requests.get(
        f"{BASE_URL}/company/06993349",  # Los Romeros Limited
        auth=(API_KEY, ""),
        timeout=15
    )
    print(f"\n  API test (Los Romeros 06993349): HTTP {test_resp.status_code}")
    if test_resp.status_code == 200:
        data = test_resp.json()
        print(f"  Company name: {data.get('company_name', '?')}")
        print(f"  Status: {data.get('company_status', '?')}")
        print(f"  Address: {data.get('registered_office_address', {})}")
    elif test_resp.status_code == 401:
        print("  API key rejected — will use web scrape data only (no director lookup)")
    print()

    rows_written = 0
    los_romeros_found = False

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Company Name",
            "Company Number",
            "Status",
            "Type",
            "Date Incorporated",
            "Date Dissolved",
            "SIC Codes",
            "Registered Address",
            "Director Name",
            "Director Role",
            "Director Correspondence Address (LEAD)",
            "Director Appointed",
        ])

        for i, company in enumerate(companies_list):
            num = company["company_number"]
            display_name = company.get("company_name", num)

            sys.stdout.write(f"\r  [{i+1:3d}/{len(companies_list)}] {display_name[:52]:<52}")
            sys.stdout.flush()

            if "LOS ROMEROS" in display_name.upper():
                los_romeros_found = True
                print(f"\n  *** CONFIRMED: LOS ROMEROS LIMITED ({num}) found in dataset ***")

            # Get company detail
            detail = fetch_company_detail(num) if test_resp.status_code == 200 else {}
            status = detail.get("company_status", "")
            company_type = detail.get("type", "")
            date_inc = detail.get("date_of_creation", "")
            date_dis = detail.get("date_of_cessation", "")
            sic_list = detail.get("sic_codes", [])
            sic_codes = ", ".join(
                s.get("sic_code", "") if isinstance(s, dict) else str(s)
                for s in sic_list
            )
            addr_dict = detail.get("registered_office_address", {})
            reg_address = ", ".join(filter(None, [
                addr_dict.get("address_line_1", ""),
                addr_dict.get("address_line_2", ""),
                addr_dict.get("locality", ""),
                addr_dict.get("postal_code", ""),
            ]))

            directors = fetch_directors(num) if test_resp.status_code == 200 else []

            if directors:
                for d in directors:
                    writer.writerow([
                        display_name, num, status, company_type,
                        date_inc, date_dis, sic_codes, reg_address,
                        d["name"], d["role"], d["address"], d["appointed_on"],
                    ])
                    rows_written += 1
            else:
                writer.writerow([
                    display_name, num, status, company_type,
                    date_inc, date_dis, sic_codes, reg_address,
                    "NO ACTIVE DIRECTOR", "", "", "",
                ])
                rows_written += 1

            time.sleep(0.7)

    print(f"\n\n{'=' * 62}")
    print(f"[3/3] COMPLETE")
    print(f"{'=' * 62}")
    print(f"  Companies processed : {len(companies_list)}")
    print(f"  Rows written        : {rows_written}")
    print(f"  Output file         : {OUTPUT_FILE}")
    if los_romeros_found:
        print(f"\n  ✓ LOS ROMEROS LIMITED confirmed in dataset")
    else:
        print(f"\n  ℹ LOS ROMEROS LIMITED not found by name scrape")
        print(f"    Check company number 06993349 in the CSV manually")
    print()


if __name__ == "__main__":
    main()
