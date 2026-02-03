import sqlite3
import pandas as pd

def view_data():
    conn = sqlite3.connect('erp.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n--- TABLES FOUND ---")
    for table in tables:
        print(f"Table: {table[0]}")
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table[0]}", conn)
            print(df.head().to_string())
            print("-" * 50)
        except Exception as e:
            print(f"Empty or Error: {e}")
            
    conn.close()

if __name__ == "__main__":
    view_data()
