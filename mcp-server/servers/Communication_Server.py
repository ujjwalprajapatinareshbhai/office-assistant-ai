from fastmcp import FastMCP
from core.auth import MyTokenVerifier
from tools.prompt_tools import load_prompt

from tools.email_tools import send_email

auth = MyTokenVerifier()

mcp = FastMCP(
    "Communication Server",
    auth=auth
)

#-----------------EMAIL--------------------#

@mcp.tool()
def send_a_email(
    to: str,
    subject: str,
    body: str
):
    """
    Send an email.

    Parameters:
    - to: Recipient email address
    - subject: Email subject
    - body: Email body

    The supervisor must provide the recipient,
    subject, and body.
    """

    return send_email(
        to,
        subject,
        body
    )

#-----------------PROMPT------------------#

@mcp.prompt
def load_company_prompt(prompt_name: str):
    """Load a prompt by name."""
    return load_prompt(prompt_name)

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8004
    )