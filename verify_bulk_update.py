import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_bulk_update():
    print("Testing Bulk Rate Update Functionality...")
    
    # 1. Create a dummy item if not exists or use existing
    item_name = "BulkTestItem"
    initial_rate = 100
    
    # Ensure item exists
    payload_add = {'item': item_name, 'rate': initial_rate}
    requests.post(f'{BASE_URL}/add_item', data=payload_add)
    
    # 2. Update rate using fast API
    new_rate = 250
    print(f"Updating {item_name} rate to {new_rate}...")
    
    payload_update = {'item': item_name, 'rate': new_rate}
    res = requests.post(f'{BASE_URL}/update_rate_fast', json=payload_update)
    
    if res.json().get('status') == 'success':
        print(f"SUCCESS: Rate update request successful.")
    else:
        print(f"FAILURE: Update request failed. {res.json()}")
        return

    # 3. Verify the change by fetching rate
    res_check = requests.get(f'{BASE_URL}/get_item_rate/{item_name}')
    data = res_check.json()
    
    if int(data.get('rate')) == new_rate:
        print(f"SUCCESS: Rate verified as {data.get('rate')}.")
    else:
        print(f"FAILURE: Rate mismatch. Expected {new_rate}, got {data.get('rate')}.")

if __name__ == '__main__':
    test_bulk_update()
