"""
Adrem Accounting Victim Search — CW12 4AA
==========================================
Searches Companies House Advanced Search API for all companies registered
at postcode CW12 4AA (1-2 Albert Chambers, Canal Street, Congleton).

This is the postcode Adrem Accounting Ltd moved to in 2024-2025 and where
your father's company (Los Romeros Limited) and other migrated clients are
now registered.

Output: adrem_cw12_4aa_leads.csv
"""

import requests
import time
import csv
import sys

API_KEY = "4416608c-08ec-449e-8c5a-ddc66b5bb6b3"
BASE_URL = "https://api.company-information.service.gov.uk"
TARGET_POSTCODE = "CW12 4AA"
OUTPUT_FILE = "adrem_cw12_4aa_leads.csv"

def fetch_all_companies_at_postcode(postcode):
    """Fetch all companies registered at a given postcode using Advanced Search."""
    print(f"\n[1/3] Searching Companies House for: {postcode}")
    print(f"      (Adrem Accounting Ltd — 1-2 Albert Chambers, Canal Street, Congleton)\n")

    encoded = postcode.replace(" ", "+")
    companies = []
    start_index = 0
    page_size = 50

    while True:
        url = (
            f"{BASE_URL}/advanced-search/companies"
            f"?location={encoded}"
            f"&size={page_size}"
            f"&start_index={start_index}"
        )
        response = requests.get(url, auth=(API_KEY, ""))

        if response.status_code == 401:
            print("ERROR: API key rejected (401 Unauthorized). Check your key.")
            sys.exit(1)
        elif response.status_code == 429:
            print("Rate limited — waiting 10 seconds...")
            time.sleep(10)
            continue
        elif response.status_code != 200:
            print(f"ERROR {response.status_code}: {response.text[:200]}")
            break

        data = response.json()
        items = data.get("items", [])
        total = data.get("hits", data.get("total_results", "?"))

        if start_index == 0:
            print(f"      Total companies found at {postcode}: {total}\n")

        if not items:
            break

        for item in items:
            companies.append({
                "company_name": item.get("company_name", ""),
                "company_number": item.get("company_number", ""),
                "company_status": item.get("company_status", ""),
                "company_type": item.get("company_type", ""),
                "date_of_creation": item.get("date_of_creation", ""),
                "registered_office_address": item.get("registered_office_address", {})
            })

        print(f"  Fetched {len(companies)} companies so far... (page start={start_index})")
        start_index += page_size

        if len(items) < page_size:
            break  # Last page

        time.sleep(0.5)

    return companies


def fetch_directors(company_number):
    """Fetch director names and correspondence addresses for a company."""
    url = f"{BASE_URL}/company/{company_number}/officers"
    try:
        response = requests.get(url, auth=(API_KEY, ""))
        if response.status_code != 200:
            return []

        directors = []
        for item in response.json().get("items", []):
            role = item.get("officer_role", "")
            if "director" not in role.lower():
                continue
            if item.get("resigned_on"):
                continue  # Skip resigned directors

            addr = item.get("address", {})
            address_parts = [
                addr.get("address_line_1", ""),
                addr.get("address_line_2", ""),
                addr.get("locality", ""),
                addr.get("region", ""),
                addr.get("postal_code", ""),
                addr.get("country", ""),
            ]
            address_str = ", ".join(p for p in address_parts if p)

            directors.append({
                "name": item.get("name", ""),
                "role": role,
                "address": address_str,
                "appointed_on": item.get("appointed_on", "")
            })

        return directors
    except Exception as e:
        return []


def main():
    print("=" * 60)
    print("  ADREM ACCOUNTING VICTIM SEARCH — CW12 4AA")
    print("=" * 60)

    companies = fetch_all_companies_at_postcode(TARGET_POSTCODE)

    if not companies:
        print("\nNo companies returned. Check API key and postcode.")
        return

    print(f"\n[2/3] Fetching directors for {len(companies)} companies...\n")

    rows_written = 0
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Company Name",
            "Company Number",
            "Status",
            "Type",
            "Date of Creation",
            "Registered Office",
            "Director Name",
            "Director Role",
            "Director Address (LEAD)",
            "Director Appointed"
        ])

        for i, company in enumerate(companies):
            num = company["company_number"]
            name = company["company_name"]
            sys.stdout.write(f"\r  Processing [{i+1}/{len(companies)}]: {name[:50]:<50}")
            sys.stdout.flush()

            addr_dict = company.get("registered_office_address", {})
            reg_office = ", ".join(filter(None, [
                addr_dict.get("address_line_1", ""),
                addr_dict.get("locality", ""),
                addr_dict.get("postal_code", "")
            ]))

            directors = fetch_directors(num)

            if directors:
                for d in directors:
                    writer.writerow([
                        name,
                        num,
                        company["company_status"],
                        company["company_type"],
                        company["date_of_creation"],
                        reg_office,
                        d["name"],
                        d["role"],
                        d["address"],
                        d["appointed_on"]
                    ])
                    rows_written += 1
            else:
                # Write company row with no director found
                writer.writerow([
                    name, num,
                    company["company_status"],
                    company["company_type"],
                    company["date_of_creation"],
                    reg_office,
                    "NO DIRECTOR FOUND", "", "", ""
                ])
                rows_written += 1

            time.sleep(0.5)

    print(f"\n\n[3/3] DONE.")
    print(f"\n  Companies processed : {len(companies)}")
    print(f"  Total rows written  : {rows_written}")
    print(f"  Output file         : {OUTPUT_FILE}")
    print(f"\n  Search for 'LOS ROMEROS' or 'HARRISON' in the output to verify")
    print(f"  your father's company is captured in this dataset.\n")


if __name__ == "__main__":
    main()
