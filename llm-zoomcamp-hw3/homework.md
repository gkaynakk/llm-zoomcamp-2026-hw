# Question 1: Context Engineering
After trying the same prompt in ChatGPT vs Kestra's AI Copilot, what is the primary reason AI Copilot generates better Kestra flows?


Answer: AI Copilot has access to current Kestra plugin documentation

# Question 2: RAG vs No RAG
Run both 1_chat_without_rag.yaml and 2_chat_with_rag.yaml in the Kestra UI. Read the execution logs for each.

The non-RAG response about Kestra 1.1 features is best described as:


Vague, generic, or fabricated — the model guesses from training data


# Question 3: Token usage — short summary
What is the approximate output token count for multilingual_agent?

Answer : - Output tokens: 83

# Question 4: Token usage — long summary
Compare the multilingual_agent output token count to your result from Question 3. Roughly how many times more output tokens does the long summary use?

Answer : - Output tokens: 207

# Question 5: Modifying a flow

Compare the english_brevity output token count to the original 1-sentence version (also with summary_length = long). How do they compare?
original 42
Answer: - Output tokens: 75

# Question 6: Best Practices
Based on what you learned in this module, for production workflows requiring deterministic, repeatable results with strict compliance requirements (e.g., financial reporting, workflows in highly regulated industries), which approach is most appropriate?

Answer: Use traditional task-based workflows for predictability and auditability