import sqlite3


import os

def init_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_NAME = os.path.join(BASE_DIR, 'Billing.db')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Menu table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Menu (
            item TEXT PRIMARY KEY,
            rate REAL
        )
    ''')
    
    # Create Headwaiter table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Headwaiter (
            waiter TEXT PRIMARY KEY
        )
    ''')

    # Create SaleInvMaster table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SaleInvMaster (
            InvNo INTEGER PRIMARY KEY,
            InvDate TEXT,
            InvTime TEXT,
            Amount REAL,
            CGSTPer REAL,
            CGST REAL,
            SGSTPer REAL,
            SGST REAL,
            Adjustment REAL,
            NetAmount REAL,
            Remark TEXT,
            AmtInWords TEXT,
            TableNo TEXT,
            Waiter TEXT
        )
    ''')

    # Create SaleInvDetails table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SaleInvDetails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            InvNo INTEGER,
            Item TEXT,
            Rate REAL,
            Qty INTEGER,
            Amount REAL,
            FOREIGN KEY(InvNo) REFERENCES SaleInvMaster(InvNo)
        )
    ''')
    
    # Create KOT table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS KOT (
            EntryNo INTEGER PRIMARY KEY AUTOINCREMENT,
            EntryDate TEXT,
            EntryTime TEXT,
            TableNo TEXT,
            Item TEXT,
            Qty INTEGER,
            BillMade TEXT DEFAULT 'No',
            KOTPrinted TEXT DEFAULT 'No'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
