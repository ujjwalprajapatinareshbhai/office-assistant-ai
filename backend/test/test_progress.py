import asyncio
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


URL = "http://127.0.0.1:8000/mcp"

HEADERS = {
    "Authorization": "Bearer my-super-secret-key-123"
}


async def progress_callback(progress: float, total: float | None, message: str | None):
    if total:
        print(f"📄 Progress: {progress}/{total}", flush=True)
    else:
        print(f"📄 Progress: {progress}", flush=True)

    if message:
        print(f"   {message}", flush=True)


async def main():

    async with httpx.AsyncClient(
        headers=HEADERS
    ) as http_client:

        async with streamable_http_client(
            URL,
            http_client=http_client
        ) as (read_stream, write_stream, _):

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                await session.initialize()

                print("Connected to MCP server.")

                result = await session.call_tool(
                    "search_from_all_files",
                    arguments={
                        "keyword": "company"
                    },
                    progress_callback=progress_callback
                )

                print("\nTool result:")
                print(result)


if __name__ == "__main__":
    asyncio.run(main())