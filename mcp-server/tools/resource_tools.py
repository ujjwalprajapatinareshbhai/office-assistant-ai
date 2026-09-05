from pathlib import Path

FILES_DIR = Path("files")


def read_resource_file(filename:str):
    """Read any file from the directory"""
    path = (FILES_DIR/filename).resolve()

    if not str(path).startswith(str(FILES_DIR.resolve())):
        return "Access denied"

    if not path.exists():
        return f"{filename} not found"
    
    return path.read_text(encoding="utf-8")