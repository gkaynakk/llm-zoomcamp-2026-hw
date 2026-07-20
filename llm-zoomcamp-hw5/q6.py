import sqlite3
import pandas as pd

conn = sqlite3.connect("traces.db")

df = pd.read_sql_query("""
SELECT input_tokens
FROM spans
WHERE name = 'llm'
""", conn)

conn.close()

print(df)