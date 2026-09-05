from fastmcp import FastMCP
from core.auth import MyTokenVerifier

from tools.pdf_reader import read_pdf
from tools.excel_reader import read_excel

auth = MyTokenVerifier()

mcp = FastMCP(
    "Document Server",
    auth=auth
)

# ---------------- PDF ----------------

@mcp.tool()
def get_pdf_reader(filename: str):
    """Read the PDF file."""
    return read_pdf(filename)


# ---------------- Excel ----------------

@mcp.tool()
def get_excel_reader(filename: str):
    """Read the Excel file."""
    return read_excel(filename)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8003
    )