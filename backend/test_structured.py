import asyncio
from typing import List

from pydantic import BaseModel
from langchain_ollama import ChatOllama


class Task(BaseModel):
    id: str
    tool: str
    arguments: dict
    depends_on: List[str]


class Plan(BaseModel):
    reason: str
    tasks: List[Task]


async def main():

    llm = ChatOllama(
        model="gemma4:cloud",
        temperature=0,
    )

    structured_llm = llm.with_structured_output(
        Plan
    )

    prompt = """
You are a supervisor.

User request:
what is the leave policy

Available tool:
search_files_content

Create one task to search for the leave policy.
"""

    print("Calling Gemma 4 Cloud...")

    try:

        result = await asyncio.wait_for(
            structured_llm.ainvoke(prompt),
            timeout=120,
        )

        print("\n========== RESULT ==========")
        print(result)

        print("\n========== TYPE ==========")
        print(type(result))

        print("\n========== DICT ==========")
        print(result.model_dump())

    except asyncio.TimeoutError:

        print("\n❌ TIMEOUT")

    except Exception as e:

        print("\n❌ ERROR")
        print(type(e).__name__)
        print(repr(e))


asyncio.run(main())