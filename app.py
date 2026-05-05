import streamlit as st
from dq_engine import read_rules, generate_sql_llm, run_query, interpret_result_llm
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

st.title("🤖 AI Data Quality Assistant")

user_input = st.text_input("Ask about your data quality:")

if user_input:
    st.write(f"🔍 You asked: {user_input}")

    # Connect DB
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )

    rules = read_rules("cde_rules.txt")

    matched = False

    for rule in rules:
        cde = rule["cde"]

        if cde.lower() in user_input.lower():
            matched = True

            sql = generate_sql_llm(rule["table"], cde, rule["rule"])
            result = run_query(conn, sql)
            message = interpret_result_llm(cde, rule["rule"], result)

            st.success(message)

    if not matched:
        st.warning("No matching CDE found. Try: revenue, cost, profit")

    conn.close()