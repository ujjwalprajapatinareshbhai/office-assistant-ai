from fastmcp import FastMCP,Context
from core.auth import MyTokenVerifier
import time

from tools.file_tools import (
    read_file,
    list_files,
    write_file,
    append_file,
    rename_file,
    delete_file,
    search_files
)
from tools.folder_tools import (create_folder,delete_folder,move_file)
from tools.notes_tools import(append_note,read_notes)
from tools.report_tools import (create_report)
from tools.resource_tools import(read_resource_file)

from tools.search_tools import search,search_all_file
auth = MyTokenVerifier()

mcp = FastMCP(
    "Office Server",
    auth=auth
)

@mcp.tool()
def get_file(file_name: str):
    """Read files from office folder."""
    return read_file(file_name)


@mcp.tool()
def get_file_list():
    """List files in office folder."""
    print("✅ MCP TOOL CALLED")
    return list_files()


@mcp.tool()
def create_file(file_name: str, content: str):
    """Create a file in the office folder."""
    return write_file(file_name, content)


@mcp.tool()
def append_to_file(file_name: str, content: str):
    """Append content to a file."""
    return append_file(file_name, content)


@mcp.tool()
def rename_to_file(old_name: str, new_name: str):
    """Rename a file."""
    return rename_file(old_name, new_name)


@mcp.tool()
def search_files_content(keyword: str):
    """
    Search office files by filename or file content.

    Returns matching file names and match information.
    The returned file_name can be used with get_file
    to retrieve the complete file contents.
    """
    return search_files(keyword)


@mcp.tool()
def delete_a_file(file_name: str):
    """Delete a file."""
    return delete_file(file_name)

#-----------------FOLDER_TOOL-----------------#

@mcp.tool()
def create_folder_tool(folder_name: str):
    """Create a new folder"""
    return create_folder(folder_name)

@mcp.tool()
def delete_folder_tool(folder_name: str):
    """Delete a folder."""
    return delete_folder(folder_name)

@mcp.tool()
def move_file_tool(file_name: str, folder: str):
    """Move a file from one folder to another."""
    return move_file(file_name, folder)

#------------------NOTES_TOOL-----------------#

@mcp.tool()
def append_note_tool(text: str):
    """Add the new text into the existing file"""
    return append_note(text)

@mcp.tool()
def read_note_tool():
    """Read the text from the notes"""
    return read_notes()
#-------------------REPORT_TOOL---------------#

@mcp.tool()
def generate_report_tool(
    title: str, summary: str, details: str = "", sources: list[str] | None = None
):
    """Generate a formatted report that can be displayed or emailed."""
    return create_report(title, summary, details, sources)

#--------------------RESOURCE----------------------#

@mcp.resource("files://{filename}")
def file_resource(filename: str):
    """Read any file from the files directory."""
    return read_resource_file(filename)

#-------------------STREAM_DEMO---------------------#

@mcp.tool()
def stream_demo():
    """Demonstrates streaming."""

    yield "🚀 Starting..."

    time.sleep(2)

    yield "📂 Reading files..."

    time.sleep(2)

    yield "🌐 Searching..."

    time.sleep(2)

    yield "📝 Creating report..."

    time.sleep(2)

    yield "✅ Done!"

#--------------------CONTEXT_DEMO-------------------#

@mcp.tool()
def context_demo(name: str, ctx: Context):
    """Simple context demo."""

    ctx.info(f"context_demo called with name={name}")
    
    return f"Hello {name}"

#-------------------WEB_SEARCH----------------------#

@mcp.tool()
def web_search(query: str):
    """Search the web for the given query."""
    return search(query)

@mcp.tool()
async def search_from_all_files(keyword: str, ctx: Context):
    """
    Search all files for a keyword.
    """
    for message in search_all_file(keyword):

        if message.message_type == "progress":
            print(f"Progress: {message.current}/{message.total}")
            await ctx.report_progress(
                progress=message.current,
                total=message.total,
                message = f"Searching {message.filename}"
            )
        elif message.message_type == "result":
            return message.data
        elif message.message_type == "error":
            raise Exception (message.error)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000
    )