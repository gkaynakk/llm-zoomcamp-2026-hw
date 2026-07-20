from starter import RAGTraced, index, client


rag = RAGTraced(
    index=index,
    llm_client=client
)

query = "How does the agentic loop keep calling the model until it stops?"

answer = rag.rag(query)

print(answer)