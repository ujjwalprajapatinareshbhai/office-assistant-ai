from typing import List

from pydantic import BaseModel, Field

from app.agent import llm

from app.memory_store import (
    save_memory,
    get_memory,
    update_memory,
)


class Memory(BaseModel):
    key: str = Field(description="Memory key")
    value: str = Field(description="Memory value")


class MemoryExtraction(BaseModel):
    memories: List[Memory]


memory_llm = llm.with_structured_output(
    MemoryExtraction
)


async def extract_memories(user_message: str):

    prompt = f"""
You are an intelligent memory extraction system.

Extract ONLY information that should be remembered
for future conversations.

Examples:

User:
My name is John.

Memory:
name = John

------------------------

User:
I live in Pune.

Memory:
city = Pune

------------------------

User:
I work at Google.

Memory:
company = Google

------------------------

User:
My favourite language is Python.

Memory:
favorite_language = Python

------------------------

User:
My birthday is 27 September.

Memory:
birthday = 27 September

------------------------

Ignore temporary requests like:

Hello

Thank you

Search this PDF

Delete employee 5

Open notes.txt

What's the weather today

Return ONLY structured memories.

User Message:

{user_message}
"""

    result = await memory_llm.ainvoke(prompt)

    return result.memories


async def remember(
    user_id: str,
    user_message: str
):
    """
    Extract memories and intelligently
    insert or update them.
    """

    memories = await extract_memories(user_message)

    for memory in memories:

        existing_value = get_memory(
            user_id,
            memory.key
        )

        if existing_value is None:

            print(
                f"💾 Saving memory: "
                f"{memory.key} = {memory.value}"
            )

            save_memory(
                user_id,
                memory.key,
                memory.value
            )

        elif existing_value != memory.value:

            print(
                f"🔄 Updating memory: "
                f"{memory.key}"
            )

            update_memory(
                user_id,
                memory.key,
                memory.value
            )

        else:

            print(
                f"✅ Memory already exists: "
                f"{memory.key}"
            )

    return memories

if __name__ == "__main__":

    import asyncio

    async def main():

        memories = await remember(
            "user1",
            "My name is Ujjwal. I live in Pune and my favourite language is Python."
        )

        print()

        for memory in memories:
            print(memory)

    asyncio.run(main())