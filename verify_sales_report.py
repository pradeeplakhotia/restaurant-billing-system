import requests
import json
import os
import datetime

BASE_URL = 'http://127.0.0.1:5000'

def test_sales_report():
    print("Testing Sales Report Generation...")
    
    today = datetime.date.today().isoformat()
    
    # 1. Complete Report
    print("Testing 'Complete' Report...")
    payload_complete = {
        'type': 'complete',
        'start_date': '',
        'end_date': '',
        'waiter': ''
    }
    res = requests.post(f'{BASE_URL}/generate_sales_report', json=payload_complete)
    data = res.json()
    if data.get('status') == 'success' and 'sales_report_complete.pdf' in data.get('pdf_url'):
        print("SUCCESS: Complete Report generated.")
    else:
        print(f"FAILURE: Complete Report failed. {data}")

    # 2. Datewise Report
    print("Testing 'Datewise' Report...")
    payload_date = {
        'type': 'datewise',
        'start_date': today,
        'end_date': today,
        'waiter': ''
    }
    res = requests.post(f'{BASE_URL}/generate_sales_report', json=payload_date)
    data = res.json()
    if data.get('status') == 'success' and 'sales_report_datewise.pdf' in data.get('pdf_url'):
        print("SUCCESS: Datewise Report generated.")
    else:
        print(f"FAILURE: Datewise Report failed. {data}")

    # 3. Waiterwise Report
    print("Testing 'Waiterwise' Report...")
    # Need a valid waiter name. Using 'W1' (from previous tests) or just dummy check.
    payload_waiter = {
        'type': 'waiterwise',
        'start_date': today,
        'end_date': today,
        'waiter': 'Test Waiter'
    }
    res = requests.post(f'{BASE_URL}/generate_sales_report', json=payload_waiter)
    data = res.json()
    if data.get('status') == 'success' and 'sales_report_waiterwise.pdf' in data.get('pdf_url'):
        print("SUCCESS: Waiterwise Report generated.")
    else:
        print(f"FAILURE: Waiterwise Report failed. {data}")

if __name__ == '__main__':
    test_sales_report()
