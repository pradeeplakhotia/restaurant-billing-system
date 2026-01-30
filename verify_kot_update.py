import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_update_kot():
    print("Testing KOT Update...")
    
    # 1. Get an existing entry (or create one)
    # Let's create a specific one for testing update
    payload_save = {
        'action': 'save',
        'date': '01-Jan-2026',
        'time': '12:00 PM',
        'tableNo': 'T-UPDATE-TEST',
        'item': 'Original Item',
        'qty': 1
    }
    requests.post(f'{BASE_URL}/kot_action', json=payload_save).json()
    
    # Get it back to find EntryNo
    res = requests.get(f'{BASE_URL}/get_kot_data')
    entries = res.json().get('entries', [])
    target_entry = None
    for e in entries:
        if e['TableNo'] == 'T-UPDATE-TEST':
            target_entry = e
            break
            
    if not target_entry:
        print("Failed to create test entry.")
        return

    print(f"Created Entry: {target_entry}")

    # 2. Update it
    payload_update = {
        'action': 'update',
        'entryNo': target_entry['EntryNo'],
        'tableNo': 'T-UPDATE-TEST',
        'item': 'Updated Item',
        'qty': 5
    }
    
    res_update = requests.post(f'{BASE_URL}/kot_action', json=payload_update)
    print(f"Update Response: {res_update.json()}")
    
    # 3. Verify
    res_ver = requests.get(f'{BASE_URL}/get_kot_data')
    entries_ver = res_ver.json().get('entries', [])
    updated = False
    for e in entries_ver:
        if e['EntryNo'] == target_entry['EntryNo']:
            print(f"Verified Entry: {e}")
            if e['Item'] == 'Updated Item' and e['Qty'] == 5:
                updated = True
            break
            
    if updated:
        print("SUCCESS: KOT Entry updated correctly.")
    else:
        print("FAILURE: KOT Entry did not update correctly.")

if __name__ == '__main__':
    test_update_kot()
