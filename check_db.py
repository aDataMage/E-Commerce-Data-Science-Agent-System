import sqlite3
import os

db_path = "ecommerce.db"
print(f"Checking DB at: {os.path.abspath(db_path)}")

if not os.path.exists(db_path):
    print("❌ Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("❌ No tables found in database.")
else:
    print(f"✅ Found {len(tables)} tables:")
    for table in tables:
        name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        count = cursor.fetchone()[0]
        print(f"  - {name}: {count} rows")

conn.close()
