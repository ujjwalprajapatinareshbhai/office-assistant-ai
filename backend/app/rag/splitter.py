from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.loader import load_documents


# ============================================================
# TEXT SPLITTER
# ============================================================

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


# ============================================================
# SPLIT DOCUMENTS
# ============================================================

def split_documents():

    documents = load_documents()

    if not documents:

        return []

    chunks = splitter.split_documents(
        documents
    )

    return chunks


# ============================================================
# SPLIT UPLOADED DOCUMENT
# ============================================================

def split_uploaded_documents(
    documents,
):

    if not documents:

        return []

    chunks = splitter.split_documents(
        documents
    )

    return chunks


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    chunks = split_documents()

    print()

    print(
        f"Created {len(chunks)} chunks"
    )

    for i, chunk in enumerate(
        chunks,
        start=1,
    ):

        print("=" * 60)

        print(
            f"Chunk {i}"
        )

        print()

        print(
            chunk.metadata
        )

        print()

        print(
            chunk.page_content
        )

        print()