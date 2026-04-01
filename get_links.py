import ssl
import json
import base64
import urllib.request

api_key = '445f486c-a61d-49ec-be74-3e16e0fa8c83'
company_no = '06993349'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = f"https://api.company-information.service.gov.uk/company/{company_no}/filing-history?items_per_page=100"
req = urllib.request.Request(url)
base64string = base64.b64encode(f"{api_key}:".encode('utf-8')).decode('utf-8')
req.add_header('Authorization', f'Basic {base64string}')
req.add_header('Accept', 'application/json')

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        history = json.loads(response.read().decode('utf-8'))
        for item in history.get('items', []):
            date = item.get('date', '')
            if date.startswith('2019'):
                tid = item.get('transaction_id', '')
                desc = item.get('description', '')
                cat = item.get('category', '')
                t = item.get('type', '')
                
                if tid and ('CS01' in t or 'confirmation' in desc):
                    print(f"CS01 LINK: https://find-and-update.company-information.service.gov.uk/company/{company_no}/filing-history/{tid}/document?format=pdf&download=0")
                elif tid and ('PSC' in t or 'significant' in cat):
                    print(f"PSC LINK: https://find-and-update.company-information.service.gov.uk/company/{company_no}/filing-history/{tid}/document?format=pdf&download=0")
except Exception as e:
    print(f"Error: {e}")
