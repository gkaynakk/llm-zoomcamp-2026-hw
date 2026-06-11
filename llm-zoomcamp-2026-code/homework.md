## Q1. How many lesson pages

How many lesson pages are in the dataset?

```python
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
openai_client = OpenAI()
```

```python
from gitsource import GithubRepositoryDataReader

reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id="8c1834d",
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)

files = reader.read()
```


```python
documents = []

for file in files:
    doc = file.parse()
    documents.append(doc)
```

```python
len(documents)
```
Answer : 72


## Q2. Indexing and searching

Index the documents with minsearch - make `content` a text field and
`filename` a keyword field. Then search with this query:

> How does the agentic loop keep calling the model until it stops?

What's the `filename` of the first result?

```python
from minsearch import Index

index = Index(
    text_fields=["content"],
    keyword_fields=["filename"]
)

index.fit(documents)

results = index.search(
    query="How does the agentic loop keep calling the model until it stops?",
    num_results=5
)

results[0]["filename"]
```

Answer : '01-agentic-rag/lessons/14-agentic-loop.md'


## Q3. RAG

```python
Use gpt-5.4-mini. How many input (prompt) tokens did we send to the model for
this request?
import importlib
import rag_helper

importlib.reload(rag_helper)

rag = rag_helper.RAGBase(
    index=index,
    llm_client=openai_client
)

answer, usage = rag.rag(
    "How does the agentic loop keep calling the model until it stops?"
)

print(answer)
print(usage)
```
```python
print(usage.input_tokens)
```

Answer: 7126

## Q4. Chunking

The lesson pages are long - some are thousands of characters. Long documents
make retrieval less precise: a match deep inside a page still pulls in the
whole page. A common fix is chunking: split each page into smaller,
overlapping pieces and index those instead.

gitsource has a helper for this: `chunk_documents`. It uses a sliding
window - a window of `size` characters slides across the text in steps of
`step` characters, and each window position becomes one chunk:

```python
from gitsource import chunk_documents

chunks = chunk_documents(documents, size=2000, step=1000)
```

With `size=2000` and `step=1000` (you can see the implementation
[here](https://github.com/alexeygrigorev/gitsource/blob/master/gitsource/chunking.py)):

- Each chunk is a window of `size` characters of the page.
- The window moves forward by `step` characters between chunks. Since `step`
  is smaller than `size`, consecutive chunks overlap by `size - step` (1000)
  characters, so a passage split across a boundary still appears whole in one
  of the chunks.
- Every chunk keeps the original fields (`filename`) and adds `start` (the
  offset in the page) and `content` (the chunk text).

How many chunks do you get?

```python

from gitsource import chunk_documents

chunks = chunk_documents(
    documents,
    size=2000,
    step=1000
)

len(chunks)
```
Answer: 295


## Q5. RAG with chunking

Chunking makes each request smaller, because we send a smaller context to the
LLM. Let's measure that.

Index the chunks from Q4 (same as before: `content` as a text field,
`filename` as a keyword field), point your RAG at the chunk index, and
answer the same query again - reading the input tokens the same way as in Q3.

Compare the input tokens with Q3. How many fewer input tokens does the chunked
version send?

```python
from gitsource import chunk_documents
from minsearch import Index

chunks = chunk_documents(
    documents,
    size=2000,
    step=1000
)

chunk_index = Index(
    text_fields=["content"],
    keyword_fields=["filename"]
)

chunk_index.fit(chunks)

rag = rag_helper.RAGBase(
    index=chunk_index,
    llm_client=openai_client
)

answer, usage = rag.rag(
    "How does the agentic loop keep calling the model until it stops?"
)

print(usage.input_tokens)

```

```python

7126 / usage.input_tokens

```

Answer : 3

## Q6. Turning it into an agent

So far search runs once, with the exact query. Let's make it agentic: give
the LLM a `search` tool and let it decide when (and what) to search. We
suggest [toyaikit](https://github.com/alexeygrigorev/toyaikit), the small
agent library from the module, but you can use anything you like - the OpenAI
Agents SDK, PydanticAI, LangChain, or a hand-written loop.

If you go with toyaikit:

```bash
uv add toyaikit
```

Create a `search` function that uses the chunk index. Give it a type hint and
a docstring - most frameworks read them to build the tool schema for you.

Build an agent with your `search` tool and run it (with toyaikit, the same way
as in the ToyAIKit lesson). Use these instructions for the agent (they nudge
it to search a few times):

> You're a course teaching assistant. Answer the student's question using the
> search tool. Make multiple searches with different keywords before answering.

Ask it:

> How does the agentic loop work, and how is it different from plain RAG?

The agent decides on its own when to search and when to answer. Count how many
times it called the `search` tool.

How many times did the agent call `search`?

```python
search_calls = 0

def search_course(query: str) -> str:
    """Search the lesson chunks."""
    
    global search_calls
    search_calls += 1

    results = chunk_index.search(
        query,
        num_results=5
    )

    return "\n\n".join(
        doc["content"]
        for doc in results
    )

```

```python
search_calls = 0

class CourseTools:
    def search_course(self, query: str) -> str:
        """Search the course lesson chunks for information relevant to the query."""
        global search_calls
        search_calls += 1

        results = chunk_index.search(
            query,
            num_results=5
        )

        lines = []

        for doc in results:
            lines.append(f"FILE: {doc['filename']}")
            lines.append(doc["content"])
            lines.append("")

        return "\n".join(lines)

```

```python
from toyaikit.tools import Tools

course_tools = CourseTools()

tools = Tools()
tools.add_tools(course_tools)


```


```python
from toyaikit.chat import ChatAssistant, OpenAIClient, IPythonChatInterface
from toyaikit.tools import Tools

course_tools = CourseTools()

tools = Tools()
tools.add_tools(course_tools)

assistant = ChatAssistant(
    tools=tools,
    developer_prompt="""
You're a course teaching assistant.
Answer the student's question using the search tool.
Make multiple searches with different keywords before answering.
""",
    chat_interface=IPythonChatInterface(),
    llm_client=OpenAIClient(model="gpt-5.4-mini")
)


```


```python
search_calls = 0

result = assistant.runner.loop(
    prompt="How does the agentic loop work, and how is it different from plain RAG?",
    previous_messages=[],
)

print(result)
print("Search calls:", search_calls)


```

Answer : 4
