import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_edit_invoice():
    print("Testing Edit Invoice Functionality...")
    
    # 1. Save Initial Invoice (InvNo 7777)
    inv_no = 7777
    print(f"Saving initial invoice {inv_no}...")
    initial_payload = {
        'master': {
            'InvNo': inv_no, 'InvDate': '2026-01-29', 'InvTime': '10:00',
            'TableNo': 'T-EDIT', 'Waiter': 'Waiter 1',
            'Amount': 100, 'CGSTPer': 0, 'CGST': 0, 'SGSTPer': 0, 'SGST': 0,
            'Adjustment': 0, 'NetAmount': 100, 'AmtInWords': 'One Hundred', 'Remark': ''
        },
        'details': [{'Item': 'Item A', 'Rate': 100, 'Qty': 1, 'Amount': 100}]
    }
    requests.post(f'{BASE_URL}/save_invoice', json=initial_payload)
    
    # 2. Verify Initial State
    res = requests.get(f'{BASE_URL}/get_invoice_details/{inv_no}').json()
    if len(res['details']) != 1:
        print("FAILURE: Initial save failed.")
        return
        
    # 3. Save UPDATED Invoice (Same InvNo)
    print("Updating invoice...")
    updated_payload = {
        'master': {
            'InvNo': inv_no, 'InvDate': '2026-01-29', 'InvTime': '11:00', # Changed Time
            'TableNo': 'T-EDIT', 'Waiter': 'Waiter 2', # Changed Waiter
            'Amount': 300, 'CGSTPer': 0, 'CGST': 0, 'SGSTPer': 0, 'SGST': 0,
            'Adjustment': 0, 'NetAmount': 300, 'AmtInWords': 'Three Hundred', 'Remark': ''
        },
        'details': [
            {'Item': 'Item A', 'Rate': 100, 'Qty': 1, 'Amount': 100},
            {'Item': 'Item B', 'Rate': 100, 'Qty': 2, 'Amount': 200} # Added Item
        ]
    }
    res_update = requests.post(f'{BASE_URL}/save_invoice', json=updated_payload)
    print(f"Update Result: {res_update.json()}")
    
    # 4. Verify Updates
    res_final = requests.get(f'{BASE_URL}/get_invoice_details/{inv_no}').json()
    master = res_final['master']
    details = res_final['details']
    
    print(f"Final Details Count: {len(details)}")
    print(f"Final Waiter: {master['Waiter']}")
    
    if len(details) == 2 and master['Waiter'] == 'Waiter 2':
        print("SUCCESS: Invoice updated correctly.")
    else:
        print("FAILURE: Invoice did not update correctly.")

if __name__ == '__main__':
    test_edit_invoice()
