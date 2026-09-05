from pathlib import Path

NOTES_FILE = Path("files") / "notes.txt"


def append_note(text: str):
    """Append a line to the office notes file."""

    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

    return "Note added successfully."


def read_notes():
    """Read all notes from the office notes file."""

    if not NOTES_FILE.exists():
        return "No notes found."

    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        return "Notes file is empty."

    return content