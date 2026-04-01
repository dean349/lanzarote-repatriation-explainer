import os
import requests

api_key = '3d5cdca1-80c1-41d3-8949-f55472f3b8e7'
company_no = '06993349'
out_dir = r"c:\DAD\UK_Lanzarote_Repatriation\Annual accounts"
session = requests.Session()
session.auth = (api_key, '')

start = 0
found = False

while not found and start < 500:
    print(f"Fetching filing history starting at {start}...")
    url = f'https://api.company-information.service.gov.uk/company/{company_no}/filing-history?items_per_page=100&start_index={start}'
    resp = session.get(url)
    if resp.status_code != 200:
        break
    history = resp.json()
    items = history.get('items', [])
    if not items:
        break
        
    for item in items:
        date = item.get('date', '')
        desc = item.get('description', '').lower()
        cat = item.get('category', '').lower()
        if date.startswith('2019') and ('person-with-significant-control' in desc or 'person with significant control' in desc or 'philip' in desc or 'significant control' in cat):
            doc_meta = item.get('links', {}).get('document_metadata', '')
            if doc_meta:
                doc_id = doc_meta.split('/')[-1]
                download_url = f"https://document-api.company-information.service.gov.uk/document/{doc_id}/content"
                print(f"Found PSC! Requesting redirect...")
                r = session.get(download_url, headers={'Accept': 'application/pdf'}, allow_redirects=False)
                if r.status_code in (301, 302, 303, 307, 308):
                    s3_url = r.headers['Location']
                    print("Downloading from S3 without auth headers...")
                    pdf_r = requests.get(s3_url)
                    with open(os.path.join(out_dir, "2019_Philip_Harrison_PSC_Ownership.pdf"), 'wb') as f:
                        f.write(pdf_r.content)
                    print("SUCCESS: Saved PSC Ownership PDF!")
                    found = True
                    break
    start += 100

print("Done.")
