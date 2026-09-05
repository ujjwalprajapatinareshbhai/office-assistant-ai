from app.rag.tools import search_knowledge_base


result = search_knowledge_base.invoke(
    "leave policy"
)

print()
print("=" * 70)
print("RAG TOOL RESULT")
print("=" * 70)
print(result)
print("=" * 70)