import requests
import datetime
import os

BASE_URL = 'http://127.0.0.1:5000'

def verify_sale_details_report():
    print("Verifying Sale Details Report...")
    
    # Ensure some data exists (assuming app is running with DB)
    # We will try to generate reports for today
    today = datetime.date.today().isoformat()
    
    # 1. Verify Summary Report
    print("1. Testing Summary Report Generation...")
    payload_summary = {
        'type': 'summary',
        'start_date': today,
        'end_date': today
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate_sale_details_report", json=payload_summary)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success' and 'pdf_url' in data:
                print(f"   PASS: Summary Report generated at {data['pdf_url']}")
                # Verify file exists
                pdf_path = data['pdf_url'].lstrip('/')
                if os.path.exists(pdf_path):
                     print("   PASS: PDF file exists on disk.")
                else:
                     print(f"   FAIL: PDF file not found at {pdf_path}")
            else:
                print(f"   FAIL: API returned error: {data.get('message')}")
        else:
            print(f"   FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   FAIL: Exception {e}")

    # 2. Verify Details Report
    print("\n2. Testing Details Report Generation...")
    payload_details = {
        'type': 'details',
        'start_date': today,
        'end_date': today
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate_sale_details_report", json=payload_details)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success' and 'pdf_url' in data:
                print(f"   PASS: Details Report generated at {data['pdf_url']}")
                # Verify file exists
                pdf_path = data['pdf_url'].lstrip('/')
                if os.path.exists(pdf_path):
                     print("   PASS: PDF file exists on disk.")
                else:
                     print(f"   FAIL: PDF file not found at {pdf_path}")
            else:
                print(f"   FAIL: API returned error: {data.get('message')}")
        else:
            print(f"   FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   FAIL: Exception {e}")

if __name__ == "__main__":
    verify_sale_details_report()
