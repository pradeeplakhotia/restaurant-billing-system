import requests
import json
import datetime

BASE_URL = 'http://127.0.0.1:5000'

def test_summary_report():
    print("Testing Summary Report Generation...")
    
    today = datetime.date.today().isoformat()
    
    # Generate Summary Report for today
    payload = {
        'start_date': today,
        'end_date': today
    }
    
    res = requests.post(f'{BASE_URL}/generate_summary_report', json=payload)
    data = res.json()
    
    if data.get('status') == 'success' and 'summary_' in data.get('pdf_url'):
        print("SUCCESS: Summary Report generated.")
    else:
        print(f"FAILURE: Report generation failed. {data}")

if __name__ == '__main__':
    test_summary_report()
