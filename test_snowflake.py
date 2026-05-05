import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

try:
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

    print("✅ Connected to Snowflake")

    cur = conn.cursor()

    # Test 1: basic query
    cur.execute("SELECT CURRENT_VERSION();")
    print("Snowflake version:", cur.fetchone())

    # Test 2: check table exists
    cur.execute("SELECT COUNT(*) FROM PANDL;")
    print("Row count in PANDL:", cur.fetchone()[0])

    # Test 3: check nulls (your DQ logic)
    cur.execute("SELECT COUNT(*) FROM PANDL WHERE REVENUE IS NULL;")
    print("Null revenue rows:", cur.fetchone()[0])

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Error connecting to Snowflake:")
    print(e)