from pathlib import Path

from langchain_chroma import Chroma

from app.agent import embeddings
from app.rag.splitter import split_documents
from app.rag.loader import load_file


# ============================================================
# VECTOR DATABASE
# ============================================================

VECTOR_DB = Path("data/chroma")

VECTOR_DB.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CREATE / LOAD VECTOR STORE
# ============================================================

def get_vector_store():

    return Chroma(
        persist_directory=str(VECTOR_DB),
        embedding_function=embeddings,
    )


# ============================================================
# ADD DOCUMENTS TO VECTOR STORE
# ============================================================

def add_documents_to_store(
    documents,
    thread_id: str | None = None,
    permanent: bool = False,
):
    """
    Add already-loaded LangChain Documents to Chroma.

    Storage modes
    -------------

    PERMANENT
        scope = "permanent"

        The document is available to every thread/user.

    TEMPORARY
        scope = "temporary"
        thread_id = current conversation/thread

        The document is available ONLY to that thread.

    IMPORTANT
    ---------

    Every chunk receives explicit metadata describing
    its visibility.

    Example permanent chunk:

        {
            "scope": "permanent",
            "source": "company_policy.pdf"
        }

    Example temporary chunk:

        {
            "scope": "temporary",
            "thread_id": "abc-123",
            "source": "private.pdf"
        }
    """

    # ========================================================
    # VALIDATE DOCUMENTS
    # ========================================================

    if not documents:

        print(
            "⚠️ No documents supplied."
        )

        return 0

    # ========================================================
    # VALIDATE TEMPORARY DOCUMENT
    # ========================================================

    if not permanent and not thread_id:

        raise ValueError(
            "thread_id is required when permanent=False."
        )

    # ========================================================
    # SET VISIBILITY METADATA
    # ========================================================

    if permanent:

        print(
            "📚 Storage mode: PERMANENT"
        )

        for document in documents:

            document.metadata["scope"] = (
                "permanent"
            )

            # Permanent documents must not belong
            # to a particular thread.

            document.metadata.pop(
                "thread_id",
                None,
            )

    else:

        print(
            "🕐 Storage mode: TEMPORARY"
        )

        print(
            "🧵 Thread ID:",
            thread_id,
        )

        for document in documents:

            document.metadata["scope"] = (
                "temporary"
            )

            document.metadata["thread_id"] = (
                thread_id
            )

    # ========================================================
    # CHUNK DOCUMENTS
    # ========================================================

    from langchain_text_splitters import (
        RecursiveCharacterTextSplitter
    )

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=100,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"📄 Documents received: {len(documents)}"
    )

    print(
        f"✂️ Created {len(chunks)} chunks"
    )

    if not chunks:

        print(
            "⚠️ No chunks were created."
        )

        return 0

    # ========================================================
    # ADD TO CHROMA
    # ========================================================

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents=chunks
    )

    print(
        f"✅ Added {len(chunks)} chunks to Chroma"
    )

    # ========================================================
    # PRINT METADATA INFORMATION
    # ========================================================

    print(
        "🔐 Document visibility:"
    )

    if permanent:

        print(
            "   scope = permanent"
        )

        print(
            "   visible = all users / all threads"
        )

    else:

        print(
            "   scope = temporary"
        )

        print(
            f"   thread_id = {thread_id}"
        )

        print(
            "   visible = current thread only"
        )

    return len(chunks)


# ============================================================
# ADD A SINGLE FILE TO VECTOR STORE
# ============================================================

def add_file_to_store(
    file_path: str,
    thread_id: str | None = None,
    permanent: bool = False,
):
    """
    Load one file and add it to Chroma.

    This function is useful for normal programmatic
    ingestion outside the HTTP upload confirmation flow.
    """

    print()
    print(
        "=========================================="
    )
    print(
        "📥 ADDING FILE TO RAG"
    )
    print(
        "=========================================="
    )

    print(
        "File:",
        file_path,
    )

    # ========================================================
    # LOAD FILE
    # ========================================================

    documents = load_file(
        file_path
    )

    if not documents:

        print(
            "⚠️ File produced no documents."
        )

        return {
            "documents": 0,
            "chunks": 0,
        }

    # ========================================================
    # ADD DOCUMENTS
    # ========================================================

    chunks_added = add_documents_to_store(

        documents,

        thread_id=thread_id,

        permanent=permanent,

    )

    return {

        "documents":
            len(documents),

        "chunks":
            chunks_added,

    }


# ============================================================
# BUILD PERMANENT VECTOR STORE
# ============================================================

def build_vector_store():
    """
    Build the permanent company knowledge base.

    Documents loaded by split_documents() are considered
    permanent company knowledge.

    They receive:

        scope = "permanent"

    and do not receive a thread_id.
    """

    chunks = split_documents()

    if not chunks:

        print(
            "⚠️ No documents found."
        )

        return None

    # ========================================================
    # MARK COMPANY DOCUMENTS AS PERMANENT
    # ========================================================

    for document in chunks:

        document.metadata["scope"] = (
            "permanent"
        )

        document.metadata.pop(
            "thread_id",
            None,
        )

    # ========================================================
    # CREATE VECTOR STORE
    # ========================================================

    vector_store = Chroma.from_documents(

        documents=chunks,

        embedding=embeddings,

        persist_directory=str(
            VECTOR_DB
        ),

    )

    print()
    print(
        "==================================="
    )

    print(
        "✅ Vector Store Created Successfully"
    )

    print(
        "==================================="
    )

    print(
        f"Stored {len(chunks)} chunks."
    )

    print(
        "🔐 Scope: permanent"
    )

    return vector_store


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    build_vector_store()