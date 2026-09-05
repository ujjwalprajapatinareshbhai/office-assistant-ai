import os

from dotenv import load_dotenv
from langchain_mcp_adapters.callbacks import Callbacks
from langchain_mcp_adapters.client import MultiServerMCPClient


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

MCP_API_KEY = os.getenv("MCP_API_KEY")

if not MCP_API_KEY:
    raise RuntimeError(
        "MCP_API_KEY is not configured. "
        "Please add MCP_API_KEY to backend/.env"
    )


# ============================================================
# MCP PROGRESS CALLBACK
# ============================================================

async def on_progress(
    progress: float,
    total: float | None,
    message: str | None,
    context,
):
    if total:
        print(
            f"\n📄 Progress: {int(progress)}/{int(total)}"
        )

    if message:
        print(f"   {message}")


callbacks = Callbacks(
    on_progress=on_progress
)


# ============================================================
# MCP CLIENT
# ============================================================

_AUTH_HEADERS = {
    "Authorization": f"Bearer {MCP_API_KEY}"
}


client = MultiServerMCPClient(
    {
        "office": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
            "headers": _AUTH_HEADERS,
        },

        "database": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8001/mcp",
            "headers": _AUTH_HEADERS,
        },

        "weather": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8002/mcp",
            "headers": _AUTH_HEADERS,
        },

        "document": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8003/mcp",
            "headers": _AUTH_HEADERS,
        },

        "communication": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8004/mcp",
            "headers": _AUTH_HEADERS,
        },

        "utility": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8005/mcp",
            "headers": _AUTH_HEADERS,
        },
    },
    callbacks=callbacks,
)