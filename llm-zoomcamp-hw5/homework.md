## Q1. First trace

Wrap the `rag()` method so each call produces a span. The simplest way
is to create a `RAGTraced` subclass of `RAGBase` that wraps `rag()`,
`search()`, and `llm()` each in their own span.

Run this query:

> How does the agentic loop keep calling the model until it stops?

The console exporter prints every finished span as a dictionary.
Count the spans in the console output - each one is a separate
`ReadableSpan` entry. How many spans does the trace produce?

```python
from starter import RAGTraced, index, client


rag = RAGTraced(
    index=index,
    llm_client=client
)

query = "How does the agentic loop keep calling the model until it stops?"

answer = rag.rag(query)

print(answer)
```


```
Answer: 3

## Q2. Capturing metrics as span attributes

Spans are not just timing markers - you can attach any information you
want to them with `set_attribute`. We already use spans to record how
long each step takes. Now we'll add the metrics we care about: tokens
and cost.

Read the token usage from the LLM response (the `llm()` method in the
starter already returns the raw response object) and set them as
attributes on the `llm` span:

```python
span.set_attribute("input_tokens", usage.input_tokens)
span.set_attribute("output_tokens", usage.output_tokens)
```

And since we know both input and output tokens, we can also compute
the cost using the code from the previous modules.

Now re-run the query. How many input tokens do we see?

```python
def llm(self, prompt):
    with tracer.start_as_current_span("llm") as span:
        response = super().llm(prompt)

        usage = response.usage

        span.set_attribute(
            "input_tokens",
            usage.input_tokens
        )

        span.set_attribute(
            "output_tokens",
            usage.output_tokens
        )

        return response
```

Answer : 7000


## Q3. Span timing

Each span automatically records its duration. Look at the console output
from Q1 and find the durations for the `search` span and the `llm` span.

For a typical query, roughly how long does the LLM call take?

    "start_time": "2026-07-20T12:32:03.226429Z",
    "end_time": "2026-07-20T12:32:05.799161Z",

Answer : Over 2000ms

## Q4. Saving traces to SQLite

Re-run the query from Q1. Which span names appear in the `spans` table?

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("traces.db")

df = pd.read_sql(
    "SELECT name FROM spans",
    conn
)

df
```

Answer: 
name
----
search
llm
rag


## Q5. Querying trace data

The traces are now in SQLite. Run one more query through the traced
RAG, then query the database.

The `rag` span wraps everything, so its duration includes both
`search` and `llm`. To see where time actually goes, exclude the
`rag` span and compare the children.

Using SQL (or pandas), compute the total duration for each span name
excluding `rag`. Which span type takes the most total time?

```python
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

```



Answer :      
name  total_duration_seconds
0     llm                5.20
1  search                0.01


## Q6. Token stability across runs

Load the SQLite data with pandas. One thing a dashboard can tell you
is how stable your system is. If the same query always produces the
same number of input tokens, the context your RAG retrieves is
consistent. If it varies a lot, something in the search may be
unstable.

Run the same query from Q1 three more times (so you have 4 RAG calls
total in the database). Then compute the input tokens for each `llm`
span.

How much do the input tokens vary across these 4 runs?


```python
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

```

Answer :  They're identical

