import os
import streamlit as st
from dq_engine import generate_sql_from_question, run_query, get_connection, format_result
from dotenv import load_dotenv

load_dotenv()

# Auto-create local DB if it doesn't exist (needed for Streamlit Cloud)
if os.getenv("USE_LOCAL_DB", "true").lower() == "true":
    if not os.path.exists("pandl.db"):
        import setup_local_db  # noqa: F401

st.title("🤖 AI Data Quality Assistant")

user_input = st.text_input("Ask about your data quality:")

if user_input:
    st.write(f"🔍 You asked: {user_input}")

    try:
        conn = get_connection()

        # Generate SQL from LLM
        sql = generate_sql_from_question(user_input)

        st.code(sql, language="sql")

        # Run query
        result = run_query(conn, sql)  

        # Format result (no LLM here)
        message = format_result(user_input, result)

        st.success(message)

    except Exception as e:
        st.error(f"Error: {str(e)}")

    finally:
        try:
            conn.close()
        except:
            pass