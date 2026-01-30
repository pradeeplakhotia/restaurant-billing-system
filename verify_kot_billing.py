import requests
import time

BASE_URL = 'http://127.0.0.1:5000'

def test_kot_billing_integration():
    print("Testing KOT to Billing Integration...")
    
    # 1. Create KOT Entries for Table T-BILL-TEST
    table_no = 'T-BILL-TEST'
    # Clear existing if any (optional, but good for clean test)
    
    print(f"Adding KOT items for {table_no}...")
    # Item 1: Test Dosa x 2
    requests.post(f'{BASE_URL}/kot_action', json={
        'action': 'save', 'date': '01-Jan-2026', 'time': '10:00 AM',
        'tableNo': table_no, 'item': 'Test Dosa', 'qty': 2
    })
    # Item 2: Test Dosa x 1 (Should aggregate to 3)
    requests.post(f'{BASE_URL}/kot_action', json={
        'action': 'save', 'date': '01-Jan-2026', 'time': '10:10 AM',
        'tableNo': table_no, 'item': 'Test Dosa', 'qty': 1
    })
    
    # 2. Fetch Pending Items
    print("Fetching pending items...")
    res = requests.get(f'{BASE_URL}/get_pending_kot_items/{table_no}')
    data = res.json()
    items = data.get('items', [])
    
    dosa_item = next((i for i in items if i['item'] == 'Test Dosa'), None)
    if dosa_item and dosa_item['qty'] == 3:
        print("SUCCESS: KOT Items fetched and aggregated correctly (Qty: 3).")
    else:
        print(f"FAILURE: Aggregation failed. Items: {items}")
        return

    # 3. Save Invoice
    print("Saving Invoice...")
    invoice_payload = {
        'master': {
            'InvNo': 9999, 'InvDate': '2026-01-27', 'InvTime': '12:00',
            'TableNo': table_no, 'Waiter': 'Test Waiter',
            'Amount': 100, 'CGSTPer': 0, 'CGST': 0, 'SGSTPer': 0, 'SGST': 0,
            'Adjustment': 0, 'NetAmount': 100, 'AmtInWords': 'One Hundred', 'Remark': ''
        },
        'details': [
            {'Item': 'Test Dosa', 'Rate': 50, 'Qty': 3, 'Amount': 150}
        ]
    }
    
    res_save = requests.post(f'{BASE_URL}/save_invoice', json=invoice_payload)
    if res_save.json().get('status') == 'success':
        print("Invoice Saved Successfully.")
    else:
        print(f"Invoice Save Failed: {res_save.json()}")
        return

    # 4. Verify KOT entries are now marked as Billed
    print("Verifying KOT entries are marked as Billed...")
    res_check = requests.get(f'{BASE_URL}/get_pending_kot_items/{table_no}')
    items_after = res_check.json().get('items', [])
    
    if len(items_after) == 0:
        print("SUCCESS: No pending items found. KOT entries marked as Billed.")
    else:
        print(f"FAILURE: Pending items still exist: {items_after}")

if __name__ == '__main__':
    test_kot_billing_integration()
