import os
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
client = OpenAI()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

RULE_FILE = os.getenv("RULE_FILE", "cde_rules.txt")

# -----------------------------
# READ RULE FILE
# -----------------------------
def read_rules(file_path):
    rules = []
    with open(file_path, "r") as f:
        block = {}
        for line in f:
            line = line.strip()
            if not line:
                if block:
                    rules.append(block)
                    block = {}
                continue

            key, value = line.split(":", 1)
            block[key.strip().lower()] = value.strip()

        if block:
            rules.append(block)

    return rules


# -----------------------------
# LLM → SQL GENERATION
# -----------------------------
def generate_sql_llm(table, column, rule):
    prompt = f"""
You are a data quality SQL generator.

Table: {table}
Column: {column}
Rule: {rule}

Generate ONLY SQL (no explanation).
Return a query that counts violations.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    # clean markdown if present
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql


# -----------------------------
# RUN QUERY
# -----------------------------
def run_query(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()[0]
    return result


# -----------------------------
# LLM → RESULT INTERPRETATION
# -----------------------------
def interpret_result_llm(cde, rule, result):
    prompt = f"""
CDE: {cde}
Rule: {rule}
Violation Count: {result}

Explain in 1 short business-friendly sentence.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


# -----------------------------
# MAIN FLOW
# -----------------------------
def main():
    print("🚀 AI Data Quality Engine Started\n")

    conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode="require"
)
    rules = read_rules(RULE_FILE)

    for rule in rules:
        cde = rule["cde"]
        table = rule["table"]
        rule_text = rule["rule"]

        print(f"➡️ Processing: {cde}")

        # LLM generates SQL
        sql = generate_sql_llm(table, cde, rule_text)
        print(f"Generated SQL:\n{sql}")

        # Execute
        result = run_query(conn, sql)

        # LLM explains result
        message = interpret_result_llm(cde, rule_text, result)

        print(f"📊 Result: {message}")
        print("-" * 50)

    conn.close()
    print("\n✅ Completed")


if __name__ == "__main__":
    main()