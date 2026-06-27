import os
import sqlite3
from dotenv import load_dotenv
import boto3
import json

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "true").lower() == "true"

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_connection():
    if USE_LOCAL_DB:
        return sqlite3.connect("pandl.db")
    else:
        import snowflake.connector
        return snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )

# -----------------------------
# LLM → SQL FROM QUESTION
# -----------------------------
def generate_sql_from_question(user_question):
    prompt = f"""
You are an AI Data Quality Assistant.

Table: PANDL

Columns:
- REVENUE (can have NULL)
- COST (can have NULL)
- PROFIT (should not be negative)

User Question:
{user_question}

Generate a SQL query compatible with SQLite.

Rules:
- For nulls → use IS NULL
- For negative values → use < 0
- Always use COUNT(*) when counting issues

Return ONLY SQL. No explanation, no markdown formatting.
"""

    body = json.dumps({
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200
    })

    response = bedrock.invoke_model(
        modelId="qwen.qwen3-coder-next",
        body=body
    )

    result = json.loads(response["body"].read())

    sql = result["choices"][0]["message"]["content"].strip()
    # Clean up markdown code fences if present
    if sql.startswith("```"):
        sql = "\n".join(sql.split("\n")[1:])
    if sql.endswith("```"):
        sql = "\n".join(sql.split("\n")[:-1])
    return sql.strip()

# -----------------------------
# RUN QUERY
# -----------------------------
def run_query(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()[0]
    cur.close()
    return result

# -----------------------------
# FORMAT RESULT (NO LLM)
# -----------------------------
def format_result(question, result):
    question = question.lower()

    if "revenue" in question:
        column = "revenue"
    elif "cost" in question:
        column = "cost"
    elif "profit" in question:
        column = "profit"
    else:
        return f"Result: {result}"

    if result == 0:
        return f"No issues found in {column} ✅"
    else:
        return f"{result} records are missing or invalid in {column}"