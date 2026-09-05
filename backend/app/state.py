from typing import Annotated, Any
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):

    messages: Annotated[
        list,
        add_messages
    ]

    next_agent: str

    routing_reason: str

    execution_plan: list[dict]

    task_results: dict[str, Any]

    active_tasks: list[str]

    completed_tasks: list[str]

    approved_tasks: list[str]

    pending_approval: dict[str, Any]

    execution_complete: bool