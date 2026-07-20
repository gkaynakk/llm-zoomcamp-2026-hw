import sqlite3
import pandas as pd

conn = sqlite3.connect("traces.db")

df = pd.read_sql_query(
    """
    SELECT
        name,
        SUM(end_time - start_time) / 1e9 AS total_duration_seconds
    FROM spans
    WHERE name != 'rag'
    GROUP BY name
    ORDER BY total_duration_seconds DESC
    """,
    conn,
)

print(df)
conn.close()