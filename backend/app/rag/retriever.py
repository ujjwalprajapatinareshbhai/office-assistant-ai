from app.rag.vector_store import get_vector_store


# ============================================================
# VECTOR STORE
# ============================================================

vector_store = get_vector_store()


# ============================================================
# SEARCH DOCUMENTS
# ============================================================

def search_documents(
    query: str,
    thread_id: str | None = None,
):
    """
    Search documents according to visibility rules.

    If thread_id exists:

        Search:
            1. Permanent documents
            2. Temporary documents belonging to this thread

    If thread_id does not exist:

        Search:
            Permanent documents ONLY.

    IMPORTANT:

    There is deliberately NO unfiltered fallback.

    This prevents a temporary document uploaded in one
    conversation from becoming visible in another conversation.
    """

    print()
    print(
        "=========================================="
    )

    print(
        "🔎 RAG SEARCH"
    )

    print(
        "=========================================="
    )

    print(
        "Query:",
        query,
    )

    print(
        "Thread ID:",
        thread_id,
    )

    # ========================================================
    # BUILD FILTER
    # ========================================================

    if thread_id:

        # ----------------------------------------------------
        # Current thread can access:
        #
        # 1. permanent documents
        # 2. temporary documents belonging to this thread
        # ----------------------------------------------------

        search_filter = {

            "$or": [

                {
                    "scope": "permanent"
                },

                {
                    "$and": [

                        {
                            "scope": "temporary"
                        },

                        {
                            "thread_id": thread_id
                        },

                    ]
                },

            ]

        }

        print(
            "🔐 Search scope:"
        )

        print(
            "   • Permanent documents"
        )

        print(
            "   • Current thread temporary documents"
        )

    else:

        # ----------------------------------------------------
        # No thread means we must NEVER search temporary
        # documents.
        # ----------------------------------------------------

        search_filter = {

            "scope": "permanent"

        }

        print(
            "🔐 Search scope:"
        )

        print(
            "   • Permanent documents ONLY"
        )

    # ========================================================
    # PERFORM SEARCH
    # ========================================================

    try:

        results = vector_store.similarity_search(

            query,

            k=3,

            filter=search_filter,

        )

        print(
            f"📚 Results found: {len(results)}"
        )

        # ====================================================
        # DEBUG RESULT METADATA
        # ====================================================

        for index, document in enumerate(

            results,

            start=1,

        ):

            print()
            print(
                f"Document {index}"
            )

            print(
                "Source:",
                document.metadata.get(
                    "source",
                    "Unknown",
                ),
            )

            print(
                "Scope:",
                document.metadata.get(
                    "scope",
                    "UNKNOWN",
                ),
            )

            print(
                "Thread:",
                document.metadata.get(
                    "thread_id",
                    "None",
                ),
            )

        return results

    except Exception as e:

        print(
            "❌ RAG search failed:",
            repr(e),
        )

        return []