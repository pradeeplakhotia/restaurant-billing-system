import requests
import os

BASE_URL = 'http://127.0.0.1:5000'

def test_reprint():
    print("Testing Reprint Functionality...")
    
    # 1. First, Save a dummy invoice to ensure we have one
    print("Saving dummy invoice...")
    payload = {
        'master': {
            'InvNo': 8888, 'InvDate': '2026-01-29', 'InvTime': '12:00',
            'TableNo': 'T-REPRINT', 'Waiter': 'Test Waiter',
            'Amount': 200, 'CGSTPer': 0, 'CGST': 0, 'SGSTPer': 0, 'SGST': 0,
            'Adjustment': 0, 'NetAmount': 200, 'AmtInWords': 'Two Hundred', 'Remark': ''
        },
        'details': [{'Item': 'Test I', 'Rate': 200, 'Qty': 1, 'Amount': 200}]
    }
    requests.post(f'{BASE_URL}/save_invoice', json=payload)
    
    # 2. Delete the PDF if it exists, to force regeneration
    pdf_path = f'static/invoices/inv_8888.pdf'
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        print("Deleted existing PDF to force regeneration.")
        
    # 3. Request Reprint
    print("Requesting Reprint...")
    res = requests.get(f'{BASE_URL}/reprint_invoice/8888')
    data = res.json()
    
    if data.get('status') == 'success':
        print(f"SUCCESS: Reprint returned success. URL: {data.get('pdf_url')}")
        if os.path.exists(pdf_path):
             print(f"SUCCESS: PDF File regenerated at {pdf_path}")
        else:
             print("FAILURE: PDF File NOT found on disk.")
    else:
        print(f"FAILURE: {data}")

if __name__ == '__main__':
    test_reprint()
