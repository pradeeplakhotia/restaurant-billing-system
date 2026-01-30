import requests
import sqlite3

BASE_URL = 'http://127.0.0.1:5000'

def test_add_item():
    print("Testing Add Item...")
    payload = {'item': 'Test Butter Chicken', 'rate': '450'}
    response = requests.post(f'{BASE_URL}/add_item', data=payload)
    if response.status_code == 200:
        print("Item added successfully (or redirected).")
    else:
        print(f"Failed to add item. Status: {response.status_code}")

def test_add_waiter():
    print("Testing Add Waiter...")
    payload = {'waiter': 'Test Waiter Suresh'}
    response = requests.post(f'{BASE_URL}/add_waiter', data=payload)
    if response.status_code == 200:
        print("Waiter added successfully (or redirected).")
    else:
        print(f"Failed to add waiter. Status: {response.status_code}")

def test_save_invoice():
    print("Testing Save Invoice...")
    # First get next inv no (simulating logic)
    # We'll just use a random one or assumed one for test
    
    import random
    inv_no = str(random.randint(2000, 9999))
    master = {
        'InvNo': inv_no,
        'InvDate': '2023-10-27',
        'InvTime': '12:00',
        'TableNo': '5',
        'Waiter': 'Test Waiter Suresh',
        'Amount': 900.0,
        'CGSTPer': 2.5,
        'CGST': 22.5,
        'SGSTPer': 2.5,
        'SGST': 22.5,
        'Adjustment': 0,
        'NetAmount': 945.0,
        'AmtInWords': 'Nine Hundred Forty Five Only',
        'Remark': 'Test Invoice'
    }
    
    details = [
        {'Item': 'Test Butter Chicken', 'Rate': 450, 'Qty': 2, 'Amount': 900}
    ]
    
    payload = {'master': master, 'details': details}
    
    response = requests.post(f'{BASE_URL}/save_invoice', json=payload)
    data = response.json()
    print(f"Response: {data}")
    
    if data.get('status') == 'success' and 'pdf_url' in data:
        print(f"PDF URL: {data['pdf_url']}")
        # Verify file exists locally (since we are on same machine)
        import os
        pdf_path = f"d:/Antigravity/Resturant{data['pdf_url']}"
        if os.path.exists(pdf_path):
            print(f"PDF file exists at: {pdf_path}")
        else:
            print(f"PDF file NOT found at: {pdf_path}")
    else:
        print("PDF generation failed or url not returned")
        return None
    return inv_no

def verify_db(inv_no):
    print("Verifying Database Content...")
    conn = sqlite3.connect('Billing.db')
    cursor = conn.cursor()
    
    print("Items:")
    for row in cursor.execute("SELECT * FROM Menu WHERE item='Test Butter Chicken'"):
        print(row)
        
    print("Waiters:")
    for row in cursor.execute("SELECT * FROM Headwaiter WHERE waiter='Test Waiter Suresh'"):
        print(row)
        
    print("Master Invoice:")
    for row in cursor.execute(f"SELECT * FROM SaleInvMaster WHERE InvNo='{inv_no}'"):
        print(row)
        
    print("Invoice Details:")
    for row in cursor.execute(f"SELECT * FROM SaleInvDetails WHERE InvNo='{inv_no}'"):
        print(row)
        
    conn.close()

if __name__ == "__main__":
    try:
        test_add_item()
        test_add_waiter()
        inv_no = test_save_invoice()
        if inv_no:
            verify_db(inv_no)
    except Exception as e:
        print(f"Error: {e}")
