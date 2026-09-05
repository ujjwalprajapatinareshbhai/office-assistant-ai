from pathlib import Path

FILES_DIR = Path("files").resolve()

def get_safe_path(file_name:str) -> Path:
    """Return a safe path for the given file name"""
    file_path = (FILES_DIR / file_name).resolve()
    if FILES_DIR not in file_path.parents and file_path != FILES_DIR:
        raise ValueError(f"Invalid file name: {file_name}")
    return file_path


def read_file(file_name:str) ->str:
    file_path = get_safe_path(file_name)

    if not file_path.exists():
        return f"file {file_name} does not exist."

    return file_path.read_text(encoding="utf-8")

def list_files() ->list[str]:
    """Return a list of files in the office folder"""
    return [
        file.name
        for file in FILES_DIR.iterdir()
        if file.is_file()
    ]

def write_file(file_name:str,content:str) ->str:
    """Write content to a file in the office folder"""
    file_path = get_safe_path(file_name)
    file_path.write_text(content,encoding="utf-8")
    return f"file {file_name} written succesfully"

def append_file(file_name:str,content:str) ->str:
    """Append the content to a file in the office folder"""
    file_path = get_safe_path(file_name)
    if not file_path.exists():
        return f"file {file_name} does not exists"
    existing = file_path.read_text(encoding = "utf-8")
    # file_path.write_text(content,encoding="utf-8",append=True)
    with open(file_path,"a" , encoding="utf-8") as file:
        if existing and not existing.endswith("\n"):
            file.write("\n")
        file.write(content)
    return f"content appended to file {file_name} successfully"

def rename_file(old_name:str,new_name:str) ->str:
    """Rename the file in the office folder"""
    old_path = get_safe_path(old_name)
    new_path = get_safe_path(new_name)

    if not old_path.exists():
        return f"File {old_name} does  not exits"
    if new_path.exists():
        return f"File {new_name} already exits"
    old_path.rename(new_path)

    return f"File {old_name} renamed to {new_name} successfully"

def search_files(keyword: str) -> list[dict]:
    """
    Search office files by filename or content.

    Returns file metadata.
    Use get_file(file_name) to retrieve the
    complete contents of a matching file.
    """

    results = []

    if not FILES_DIR.exists():
        return results

    keyword_lower = keyword.lower()

    for file in FILES_DIR.iterdir():

        if not file.is_file():
            continue

        try:
            content = file.read_text(
                encoding="utf-8"
            )
        except Exception:
            continue

        filename_match = (
            keyword_lower in file.name.lower()
        )

        content_match = (
            keyword_lower in content.lower()
        )

        if filename_match or content_match:

            results.append({
                "file_name": file.name,
                "match_type": (
                    "filename"
                    if filename_match
                    else "content"
                ),
                "instruction": (
                    "Use get_file(file_name) "
                    "to retrieve the complete file."
                )
            })

    return results  

def delete_file(file_name:str) ->str:
    """Delete a file in the office folder"""
    file_path = get_safe_path(file_name)

    if not file_path.exists():
        return f" File {file_name} does not exist"
    file_path.unlink()
    return f"File {file_name} deleted successfully"
    