import requests
from bs4 import BeautifulSoup

def main():
    xhtml_url = "https://find-and-update.company-information.service.gov.uk/company/06993349/filing-history/MzQ5NTM0Mzg5OWFkaXF6a2N4/document?format=xhtml&download=1"
    res = requests.get(xhtml_url)
    if res.status_code != 200:
        print("Download failed")
        return
        
    soup = BeautifulSoup(res.text, 'html.parser')
    print("=== EXTRACTED FINANCIALS 2025 ===")
    
    # We look for all ix:nonfraction tags
    tags = soup.find_all('ix:nonfraction')
    for tag in tags:
        context = tag.get('contextref', '')
        name = tag.get('name', '')
        val = tag.text.strip()
        
        # We only care about CURRENT_FY tags
        if 'CURRENT_FY' in context:
            print(f"{name} ({context}): £{val}")

if __name__ == "__main__":
    main()
