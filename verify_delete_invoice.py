import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_delete_invoice():
    print("Testing Delete Invoice Functionality...")
    
    # 1. Create Invoice 4444
    inv_no = 4444
    print(f"Creating Invoice {inv_no}...")
    payload_init = {
        'master': {
            'InvNo': inv_no, 'InvDate': '2026-01-29', 'InvTime': '10:00',
            'TableNo': 'T-DEL', 'Waiter': 'W1',
            'Amount': 100, 'CGSTPer': 0, 'CGST': 0, 'SGSTPer': 0, 'SGST': 0,
            'Adjustment': 0, 'NetAmount': 100, 'AmtInWords': 'One Hundred', 'Remark': ''
        },
        'details': [{'Item': 'DelItem', 'Rate': 100, 'Qty': 1, 'Amount': 100}]
    }
    requests.post(f'{BASE_URL}/save_invoice', json=payload_init)
    
    # Verify it exists
    res = requests.get(f'{BASE_URL}/get_invoice_details/{inv_no}')
    if res.json().get('status') != 'success':
        print("FAILURE: Could not create test invoice.")
        return
        
    print("Invoice created successfully.")
    
    # 2. Delete it
    print(f"Deleting Invoice {inv_no}...")
    res_del = requests.post(f'{BASE_URL}/delete_invoice/{inv_no}')
    print(f"Delete Response: {res_del.json()}")
    
    # 3. Verify it is gone
    res_check = requests.get(f'{BASE_URL}/get_invoice_details/{inv_no}')
    if res_check.json().get('status') == 'error':
        print("SUCCESS: Invoice verified deleted (not found).")
    else:
        print("FAILURE: Invoice still exists.")

if __name__ == '__main__':
    test_delete_invoice()
