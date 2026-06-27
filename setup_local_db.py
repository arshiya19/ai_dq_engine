import sqlite3

# Create local SQLite database with sample PANDL data
conn = sqlite3.connect("pandl.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS PANDL")

cur.execute("""
    CREATE TABLE PANDL (
        id INTEGER PRIMARY KEY,
        REVENUE REAL,
        COST REAL,
        PROFIT REAL
    )
""")

# Sample data with some quality issues
sample_data = [
    (1, 1000.0, 500.0, 500.0),
    (2, 2000.0, 800.0, 1200.0),
    (3, None, 600.0, -600.0),      # null revenue, negative profit
    (4, 1500.0, None, 1500.0),     # null cost
    (5, 3000.0, 1200.0, 1800.0),
    (6, None, 900.0, -900.0),      # null revenue, negative profit
    (7, 2500.0, None, 2500.0),     # null cost
    (8, 1800.0, 700.0, 1100.0),
    (9, None, 400.0, -400.0),      # null revenue, negative profit
    (10, 2200.0, 1000.0, 1200.0),
    (11, 1700.0, None, 1700.0),    # null cost
    (12, 900.0, 500.0, 400.0),
    (13, None, 300.0, -300.0),     # null revenue, negative profit
    (14, 2800.0, 1500.0, 1300.0),
    (15, 1600.0, 800.0, 800.0),
]

cur.executemany("INSERT INTO PANDL (id, REVENUE, COST, PROFIT) VALUES (?, ?, ?, ?)", sample_data)

conn.commit()
print("✅ Local PANDL table created with 15 rows")
print(f"   - Null revenue rows: 4")
print(f"   - Null cost rows: 3")
print(f"   - Negative profit rows: 4")

# Verify
cur.execute("SELECT COUNT(*) FROM PANDL")
print(f"   - Total rows: {cur.fetchone()[0]}")

conn.close()
