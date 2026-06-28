from app.ai.chain import query_chain

result = query_chain.invoke(
    "Show me all active domains"
)

print(result)