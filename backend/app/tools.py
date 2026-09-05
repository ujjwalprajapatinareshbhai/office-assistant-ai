from app.client import client
from app.rag.tools import search_knowledge_base

async def load_tools():
    tools = await client.get_tools()
    tools.append(search_knowledge_base)
    return tools