# from app.memory_store import save_memory

from app.memory_store import (
    get_memory,
    list_memories
)


def get_user_memory(
    user_id: str,
    key: str
):
    """
    Return a single memory value.
    """

    return get_memory(
        user_id,
        key
    )


def get_all_memories(
    user_id: str
):
    """
    Return all memories for a user.
    """

    return list_memories(
        user_id
    )


def build_memory_context(
    user_id: str
):
    """
    Convert all memories into text
    that can be inserted into the LLM prompt.
    """

    memories = list_memories(user_id)

    if not memories:
        return ""

    lines = []

    for key, value in memories:

        lines.append(
            f"{key}: {value}"
        )

    return "\n".join(lines)


if __name__ == "__main__":

    print()

    print(
        build_memory_context("user1")
    )