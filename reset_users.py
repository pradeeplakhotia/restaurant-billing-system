import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'Billing.db')

def reset_users():
    print(f"Connecting to {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Dropping Users table...")
    cursor.execute('DROP TABLE IF EXISTS Users')
    
    print("Recreating Users table...")
    cursor.execute('''
        CREATE TABLE Users (
            Username TEXT PRIMARY KEY,
            Password TEXT,
            Role TEXT
        )
    ''')
    
    print("Inserting default users...")
    # Add default admin
    cursor.execute("INSERT INTO Users (Username, Password, Role) VALUES ('admin', 'admin123', 'Admin')")
    # Add default waiter
    cursor.execute("INSERT INTO Users (Username, Password, Role) VALUES ('waiter', 'waiter123', 'Waiter')")
    
    conn.commit()
    conn.close()
    print("Users table reset successfully!")
    print("Default Credentials:")
    print("  Admin: admin / admin123")
    print("  Waiter: waiter / waiter123")

if __name__ == '__main__':
    try:
        reset_users()
    except Exception as e:
        print(f"Error: {e}")
