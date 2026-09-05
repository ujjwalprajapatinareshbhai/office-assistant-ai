from app.rag.retriever import search_documents


def build_rag_context(question: str) -> str:
    """
    Retrieve relevant documents and convert them
    into a text context for the LLM.
    """

    documents = search_documents(question)

    if not documents:
        return ""

    context = []

    for document in documents:

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        context.append(
            f"""
Source:
{source}

Content:
{document.page_content}
"""
        )

    return "\n\n".join(context)