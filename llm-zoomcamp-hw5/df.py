import sqlite3
import pandas as pd

conn = sqlite3.connect("traces.db")

df = pd.read_sql(
    "SELECT name FROM spans",
    conn
)

print(df)