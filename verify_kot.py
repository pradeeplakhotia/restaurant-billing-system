import requests
import sqlite3
import datetime

BASE_URL = 'http://127.0.0.1:5000'

def test_kot_flow():
    print("Testing KOT Flow...")
    
    # 1. Get Next Entry No
    try:
        res = requests.get(f'{BASE_URL}/get_next_kot_no')
        next_no = res.json().get('next_no')
        print(f"Next Entry No: {next_no}")
    except Exception as e:
        print(f"Failed to get next no: {e}")
        return

    # 2. Save KOT Entry
    date_str = datetime.datetime.now().strftime("%d-%b-%Y")
    time_str = datetime.datetime.now().strftime("%I:%M:%S %p")
    payload = {
        'action': 'save',
        'date': date_str,
        'time': time_str,
        'tableNo': 'T-99',
        'item': 'Test Dosa',
        'qty': 2
    }
    
    res = requests.post(f'{BASE_URL}/kot_action', json=payload)
    print(f"Save Response: {res.json()}")
    
    # 3. Verify Data
    res = requests.get(f'{BASE_URL}/get_kot_data')
    data = res.json()
    entries = data['entries']
    running_tables = data['running_tables']
    
    found_entry = False
    for entry in entries:
        if entry['TableNo'] == 'T-99' and entry['Item'] == 'Test Dosa':
            found_entry = True
            print(f"Found Entry in List: {entry}")
            break
            
    if found_entry:
        print("KOT Entry Saved Successfully!")
    else:
        print("KOT Entry NOT found!")
        
    if 'T-99' in running_tables:
        print("Running Table T-99 Found!")
    else:
        print("Running Table T-99 NOT Found!")

if __name__ == '__main__':
    test_kot_flow()
