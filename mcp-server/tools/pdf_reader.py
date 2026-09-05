from pathlib import Path
from pypdf import PdfReader

FILES_DIR = Path("files")

def read_pdf(filename: str):

    path = FILES_DIR / filename

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text