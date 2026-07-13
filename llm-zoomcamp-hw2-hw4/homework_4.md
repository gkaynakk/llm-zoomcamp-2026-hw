## Q1. Generating questions

Generating questions for all 72 pages costs money and takes time, so let's
start small and generate questions for just the first 3 pages:

- `01-agentic-rag/lessons/01-intro.md`
- `01-agentic-rag/lessons/02-environment.md`
- `01-agentic-rag/lessons/03-rag.md`

Each call returns the token usage, which most LLM APIs report on the response
object (e.g. `response.usage.input_tokens` / `prompt_tokens`).

What's the average number of input tokens across these 3 calls?

```python
average_input_tokens = sum(input_tokens) / len(input_tokens)

print("Token counts:", input_tokens)
print("Average:", average_input_tokens)

```

Token counts: [1021, 1287, 1754]
Average: 1354.0

Answer : 1400

## Q2. First result with text search

Take the first question from the ground truth:

```python
q = ground_truth[0]["question"]
```

After running `text_search` for it, what's the `filename` of the first result?

```python
q = ground_truth[0]["question"]

print(q)

results = text_search(q)

print(results[0]["filename"])

```

What exactly is a retrieval-augmented generation system, and why does it help with answers that the model wouldn't know on its own?
01-agentic-rag/lessons/03-rag.md

Answer: 01-agentic-rag/lessons/03-rag.md

## Q3. First result with vector search

After running `vector_search` for the same question, what's the `filename` of
the first result?

```python
q = ground_truth[0]["question"]

results = vector_search(q)

print(q)
print(results[0]["filename"])
```

answer : 01-agentic-rag/lessons/01-intro.md


## Q4. Evaluating text search

Evaluate `text_search` on the ground truth data.

What's the Hit Rate?

```python
text_metrics = evaluate(ground_truth, text_search)

print(text_metrics)
```
answer: 0.76

## Q5. Evaluating vector search

Now evaluate `vector_search` - the part we left for the homework, since the
module only evaluated keyword search.

What's the MRR?

```python
vector_metrics = evaluate(
    ground_truth,
    vector_search
)

print(vector_metrics)
```

{'hit_rate': 0.725, 'mrr': 0.5486111111111112}

answer: 0.55

## Q6. Tuning hybrid search

The `k` constant in RRF controls how much the top ranks matter. A smaller `k`
sharpens the gap between positions, so being at the top of a list counts for
more. The RRF paper uses 60 as a default, but the best value depends on the data
- so let's measure it.

Evaluate `hybrid_search` over the full ground truth dataset for `k` values 1,
50, 100, and 200. Compare the MRR values for these runs.

Which `k` gives the best MRR?

```python
for k, metrics in results.items():
    print(k, metrics["mrr"])
```

answer: 1