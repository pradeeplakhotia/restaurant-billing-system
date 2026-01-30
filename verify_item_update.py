import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_item_update_logic():
    print("Testing Invoice Item Update (Backend side)...")
    
    # 1. Setup Invoice 5555
    inv_no = 5555
    print(f"Creating Initial Invoice {inv_no}...")
    payload_init = {
        'master': {
            'InvNo': inv_no, 'InvDate': '2026-01-29', 'InvTime': '10:00',
            'TableNo': 'T-ITEM-UPD', 'Waiter': 'W1',
            'Amount': 100, 'CGSTPer': 0, 'CGST': 0, 'SGSTPer': 0, 'SGST': 0,
            'Adjustment': 0, 'NetAmount': 100, 'AmtInWords': 'One Hundred', 'Remark': ''
        },
        'details': [{'Item': 'Dosa', 'Rate': 50, 'Qty': 2, 'Amount': 100}]
    }
    requests.post(f'{BASE_URL}/save_invoice', json=payload_init)
    
    # 2. Simulate User Editing Qty from 2 to 3
    print("Simulating Edit: Updating Dosa Qty 2 -> 3...")
    payload_update = {
        'master': {
            'InvNo': inv_no, 'InvDate': '2026-01-29', 'InvTime': '10:00',
            'TableNo': 'T-ITEM-UPD', 'Waiter': 'W1',
            'Amount': 150, 'CGSTPer': 0, 'CGST': 0, 'SGSTPer': 0, 'SGST': 0,
            'Adjustment': 0, 'NetAmount': 150, 'AmtInWords': 'One Hundred Fifty', 'Remark': ''
        },
        'details': [{'Item': 'Dosa', 'Rate': 50, 'Qty': 3, 'Amount': 150}]
    }
    requests.post(f'{BASE_URL}/save_invoice', json=payload_update)
    
    # 3. Verify
    res = requests.get(f'{BASE_URL}/get_invoice_details/{inv_no}').json()
    details = res['details']
    dosa_item = details[0]
    
    if len(details) == 1 and dosa_item['Qty'] == 3 and dosa_item['Amount'] == 150:
        print("SUCCESS: Item quantity updated correctly on backend.")
    else:
        print(f"FAILURE: {details}")

if __name__ == '__main__':
    test_item_update_logic()
