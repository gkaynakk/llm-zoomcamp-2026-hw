## Q1. Embedding a query

Embed the following query:

How does approximate nearest neighbor search work?
The embedder returns a vector of 384 numbers. What's the first value (v[0])?

```python
from embedder import Embedder

embedder = Embedder()

query = "How does approximate nearest neighbor search work?"
v = embedder.encode(query)

print(len(v))
print(v[0])

```
Answer: -0.02

## Q2. Cosine similarity

The embedder returns normalized vectors, so the dot product between two of them is their cosine similarity.

Take the page 02-vector-search/lessons/07-sqlitesearch-vector.md, embed its content, and compute the cosine similarity with the query vector from Q1. What do you get?

```python
import numpy as np

similarity = np.dot(query_vector, doc_vector)

print(similarity)
```

Answer : 0.36107008472347096


## Q3. Chunking and search by hand

Which file does the highest-scoring chunk belong to (its filename)?



```python
chunks[best]
```

Answer: {'start': 1000,
 'content': 'rch. We score\nthe query against every document and pick the top ones. It always finds\nthe true top matches, but it pays for that by touching everything.\n\nApproximate nearest neighbor (ANN) search takes a shortcut. Instead of\ncomparing against everything, it first narrows down to a region of\nlikely matches. Then it scores only within that region. It may miss the\nabsolute best match, but the results are still good and it\'s much\nfaster.\n\n```text\nNN (exact):    compare query against ALL documents -> top 5\nANN (approx):  narrow down to a region -> compare within region -> top 5\n```\n\n## sqlitesearch\n\nsqlitesearch is the persistent sibling of minsearch, and it solves both\nproblems at once.\n\nWe already used it in module 1 for persistent text search. It also does\nvector search through its `VectorSearchIndex` class. It stores vectors\nin SQLite, a real on-disk database, and uses ANN strategies for\nretrieval. Because the data lives on disk, one process can write the\nvectors and another can read them back.\n\nIf you didn\'t install it in the previous module, add it to your project:\n\n```bash\nuv add sqlitesearch\n```\n\n## Creating the index\n\nInitialize it:\n\n```python\nfrom sqlitesearch import VectorSearchIndex\n\nvs_index = VectorSearchIndex(\n    keyword_fields=["course"],\n    mode="ivf",\n    db_path="faq_vectors2.db"\n)\n```\n\nsqlitesearch supports three ANN modes:\n\n- `lsh` (default): up to 100K vectors, random hyperplane projections\n- `ivf`: 10K-500K vectors, K-means clustering\n- `hnsw`: 10K-1M+ vectors, proximity graph (highest recall)\n\nFor our small dataset, `lsh` is fine. All modes use two-phase search:\napproximate candidate retrieval, then exact cosine similarity\nreranking.\n\n## Indexing the data\n\nFit the index with our vectors and documents:\n\n```python\nvs_index.fit(vectors, documents)\n```\n\nThe index is saved to `faq_vectors2.db`. Unlike minsearch, this file\npersists on disk. You can search immediately after indexing, or reopen\nthe index later without re-indexing.\n\n## Searching\n\nSearch ',
 'filename': '02-vector-search/lessons/07-sqlitesearch-vector.md'}

## Q4. Vector search with minsearch

Which file is the filename of the first result?

```python
query = "What metric do we use to evaluate a search engine?"
q = embedder.encode(query)

results = vindex.search(
    query_vector=q,
    num_results=5
)

print(results[0]["filename"])
```

Answer: 04-evaluation/lessons/05-search-metrics.md


## Q5. Text search vs vector search

Take the top 5 results from each method. Which file shows up in the vector results but not in the text results?

```python
query = "How do I store vectors in PostgreSQL?"

text_results = text_index.search(
    query,
    num_results=5
)

text_files = [r["filename"] for r in text_results]
text_files

```



Answer : 02-vector-search/lessons/08-pgvector.md


## Q6.  Hybrid search

Which file is ranked first after RRF?



```python
results = rrf([vector_results, text_results])

print(results[0]["filename"])

```

Answer : 01-agentic-rag/lessons/13-function-calling.md

