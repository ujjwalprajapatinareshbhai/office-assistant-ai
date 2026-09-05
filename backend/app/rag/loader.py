from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_core.documents import Document

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)

import pytesseract
from PIL import Image


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

# IMPORTANT:
# Do NOT hard-code:
#
# D:\Tesseract-OCR\New folder\tesseract.exe
#
# Instead, this can be configured through an environment
# variable on each computer.

TESSERACT_PATH = None

try:

    import os

    configured_path = os.getenv(
        "TESSERACT_CMD"
    )

    if configured_path:

        TESSERACT_PATH = configured_path

        pytesseract.pytesseract.tesseract_cmd = (
            configured_path
        )

except Exception:
    pass


# ============================================================
# SUPPORTED EXTENSIONS
# ============================================================

TEXT_EXTENSIONS = {
    ".txt",
}

PDF_EXTENSIONS = {
    ".pdf",
}

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".webp",
}


# ============================================================
# LOAD ONE FILE
# ============================================================

def load_file(
    file_path: str,
):

    """
    Load one file.

    Supported:

        TXT
        PDF
        PNG
        JPG
        JPEG
        BMP
        TIFF
        WEBP
    """

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"File not found: {path}"
        )

    extension = (
        path.suffix.lower()
    )

    print(
        f"📄 Loading: {path.name}"
    )

    print(
        f"📂 Type: {extension}"
    )

    # ========================================================
    # TXT
    # ========================================================

    if extension in TEXT_EXTENSIONS:

        loader = TextLoader(

            str(path),

            encoding="utf-8",
        )

        documents = loader.load()

        return documents

    # ========================================================
    # PDF
    # ========================================================

    if extension in PDF_EXTENSIONS:

        loader = PyPDFLoader(
            str(path)
        )

        documents = loader.load()

        return documents

    # ========================================================
    # IMAGE / OCR
    # ========================================================

    if extension in IMAGE_EXTENSIONS:

        return load_image_with_ocr(
            path
        )

    # ========================================================
    # UNSUPPORTED
    # ========================================================

    raise ValueError(

        f"Unsupported file type: "
        f"{extension}"
    )


# ============================================================
# OCR
# ============================================================

def load_image_with_ocr(
    path: Path,
):

    """
    Extract text from an image using Tesseract OCR.
    """

    print(
        "🔎 Running OCR..."
    )

    image = Image.open(
        path
    )

    text = pytesseract.image_to_string(
        image
    )

    if not text.strip():

        return []

    document = Document(

        page_content=text,

        metadata={
            "source": path.name,
            "type": "image",
            "ocr": True,
        },
    )

    print(
        "✅ OCR completed."
    )

    print(
        f"Extracted characters: {len(text)}"
    )

    return [
        document
    ]


# ============================================================
# LOAD PERMANENT DOCUMENTS
# ============================================================

DOCUMENTS_DIR = Path(
    "documents"
)


def load_documents():

    """
    Load files from the permanent
    documents folder.

    This is only for permanent company
    knowledge.

    Uploaded temporary files do NOT need
    to be placed here.
    """

    documents = []

    if not DOCUMENTS_DIR.exists():

        print(
            "⚠️ Documents folder not found."
        )

        return documents

    for path in DOCUMENTS_DIR.iterdir():

        if not path.is_file():

            continue

        try:

            docs = load_file(
                str(path)
            )

            documents.extend(
                docs
            )

        except Exception as e:

            print(
                f"⚠️ Failed to load "
                f"{path.name}: {e}"
            )

    return documents


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    docs = load_documents()

    print()

    print(
        f"Loaded {len(docs)} documents"
    )

    for doc in docs:

        print(
            "=" * 60
        )

        print(
            doc.metadata
        )

        print()

        print(
            doc.page_content[:500]
        )

        print()