from contextvars import ContextVar

from langchain_core.tools import tool

from app.rag.retriever import search_documents


# ============================================================
# CURRENT THREAD
# ============================================================

_current_thread_id = ContextVar(
    "rag_current_thread_id",
    default=None,
)


# ============================================================
# SET CURRENT THREAD
# ============================================================

def set_current_thread_id(
    thread_id: str | None,
):
    """
    Set the thread ID used by the RAG system.

    ContextVar is used instead of a normal global variable
    so different async requests do not accidentally overwrite
    each other's thread ID.
    """

    _current_thread_id.set(
        thread_id
    )

    print(
        "🧵 RAG current thread:",
        thread_id,
    )


# ============================================================
# GET CURRENT THREAD
# ============================================================

def get_current_thread_id():

    return _current_thread_id.get()


# ============================================================
# RAG SEARCH TOOL
# ============================================================

@tool
def search_knowledge_base(
    query: str,
) -> str:
    """
    Search the company's internal knowledge base and
    documents available to the current conversation.

    Permanent documents:
        Available to all users.

    Temporary documents:
        Available only to the current conversation.

    Use this tool for:

    - company policies
    - employee handbook
    - holidays
    - meetings
    - internal documents
    - uploaded PDF files
    - uploaded TXT files
    - uploaded DOCX files
    - uploaded images
    - OCR extracted information
    - other knowledge stored in the RAG system
    """

    # ========================================================
    # GET CURRENT THREAD
    # ========================================================

    thread_id = get_current_thread_id()

    print()
    print(
        "=========================================="
    )

    print(
        "🧠 SEARCH KNOWLEDGE BASE TOOL"
    )

    print(
        "=========================================="
    )

    print(
        "Query:",
        query,
    )

    print(
        "Thread:",
        thread_id,
    )

    # ========================================================
    # SEARCH
    # ========================================================

    docs = search_documents(

        query=query,

        thread_id=thread_id,

    )

    # ========================================================
    # NO RESULTS
    # ========================================================

    if not docs:

        return (
            "No relevant information was found "
            "in the knowledge base or in the documents "
            "available to this conversation."
        )

    # ========================================================
    # FORMAT RESULTS
    # ========================================================

    results = []

    for i, doc in enumerate(

        docs,

        start=1,

    ):

        source = doc.metadata.get(

            "source",

            "Unknown source",

        )

        scope = doc.metadata.get(

            "scope",

            "unknown",

        )

        # ----------------------------------------------------
        # Do not expose the internal thread ID to the LLM.
        # ----------------------------------------------------

        results.append(

            f"Document {i}\n"
            f"Source: {source}\n"
            f"Scope: {scope}\n"
            f"Content:\n"
            f"{doc.page_content}"

        )

    return (
        "\n\n"
        +
        "\n\n".join(
            results
        )
    )