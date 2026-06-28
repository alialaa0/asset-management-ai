from app.ai.intent import intent_chain

examples = [
    "Show all active domains",
    "Analyze api.example.com",
    "Generate inventory report",
    "Classify api.example.com",
]

for question in examples:

    result = intent_chain.invoke(question)

    print(question)

    print(result)

    print("-" * 50)