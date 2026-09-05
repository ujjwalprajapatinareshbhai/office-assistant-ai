import os

from dotenv import load_dotenv
from fastmcp.server.auth import TokenVerifier, AccessToken


load_dotenv()

API_KEY = os.getenv("MCP_API_KEY")


class MyTokenVerifier(TokenVerifier):

    async def verify_token(self, token: str) -> AccessToken | None:

        if token == API_KEY:
            return AccessToken(
                token=token,
                client_id="cursor",
                scopes=[],
            )

        return None