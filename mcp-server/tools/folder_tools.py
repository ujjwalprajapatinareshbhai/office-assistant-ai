import shutil
from pathlib import Path

FILES_DIR = Path("files")


def create_folder(folder_name: str):
    """Create a folder inside the office files directory."""

    path = FILES_DIR / folder_name

    if path.exists():
        return f"Folder '{folder_name}' already exists."

    path.mkdir(parents=True)

    return f"Folder '{folder_name}' created successfully."


def delete_folder(folder_name: str):
    """Delete a folder from the office files directory."""

    path = FILES_DIR / folder_name

    if not path.exists():
        return f"Folder '{folder_name}' does not exist."

    shutil.rmtree(path)

    return f"Folder '{folder_name}' deleted successfully."


def move_file(file_name: str, folder: str):
    """Move a file into a folder inside the office files directory."""

    source = FILES_DIR / file_name
    destination_folder = FILES_DIR / folder
    destination = destination_folder / file_name

    if not source.exists():
        return f"File '{file_name}' does not exist."

    if not destination_folder.exists():
        return f"Folder '{folder}' does not exist."

    shutil.move(str(source), str(destination))

    return f"Moved '{file_name}' to '{folder}'."