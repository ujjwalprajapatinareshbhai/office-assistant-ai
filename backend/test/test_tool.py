import asyncio
from app.tools import load_tools

async def main():
    tools = await load_tools()

    print(f"Loaded {len(tools)} tools\n")

    for tool in tools:
        print(tool.name)

asyncio.run(main())