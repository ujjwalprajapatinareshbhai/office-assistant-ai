from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.types import interrupt

from app.state import AgentState
from app.nodes import chatbot
from app.agents.supervisor import supervisor
from app.task_executor import TaskExecutor


# =====================================================
# TASK EXECUTOR NODE
# =====================================================

async def execute_tasks(
    state,
    config,
):

    tools = config[
        "configurable"
    ]["tools"]

    execution_plan = state.get(
        "execution_plan",
        []
    )

    previous_results = state.get(
        "task_results",
        {}
    )

    previous_approved = state.get(
        "approved_tasks",
        []
    )

    # =================================================
    # NO EXECUTION PLAN
    # =================================================

    if not execution_plan:

        return {
            "task_results": {},

            "approved_tasks": [],

            "pending_approval": None,

            "completed_tasks": [],

            "execution_complete": True,
        }

    print(
        "\n⚙️ TASK EXECUTOR"
    )

    executor = TaskExecutor(
        tools
    )

    # =================================================
    # EXECUTE PLAN
    # =================================================

    result = await executor.execute_plan(

        execution_plan,

        previous_results=previous_results,

        previous_approved=previous_approved,
    )

    task_results = result[
        "task_results"
    ]

    # =================================================
    # COMPLETED TASKS
    # =================================================

    completed_tasks = [

        task_id

        for task_id, task_result
        in task_results.items()

        if (
            isinstance(
                task_result,
                dict
            )

            and task_result.get(
                "success"
            )
        )
    ]

    return {

        "task_results":
            task_results,

        "approved_tasks":
            result[
                "approved_tasks"
            ],

        "pending_approval":
            result[
                "pending_approval"
            ],

        "completed_tasks":
            completed_tasks,

        "execution_complete":
            result[
                "execution_complete"
            ],
    }


# =====================================================
# APPROVAL NODE
# =====================================================

def approval_node(state):

    pending = state.get(
        "pending_approval"
    )

    # =================================================
    # SAFETY CHECK
    # =================================================

    if not pending:

        return {
            "pending_approval": None,
        }

    # =================================================
    # HUMAN INTERRUPT
    #
    # The API receives this value and sends it to React.
    #
    # React does NOT need to know internal task/tool names.
    # =================================================

    approval = interrupt(
        pending
    )

    # =================================================
    # CHECK APPROVAL
    # =================================================

    approved = (

        approval

        and str(
            approval
        ).strip().lower()

        in {
            "yes",
            "y",
            "approve",
            "approved",
        }
    )

    # =================================================
    # REJECTED
    # =================================================

    if not approved:

        print(
            "\n❌ Tool execution cancelled."
        )

        return {

            "pending_approval":
                None,

            "execution_complete":
                True,
        }

    # =================================================
    # APPROVED
    # =================================================

    task_id = pending[
        "task_id"
    ]

    approved_tasks = list(
        state.get(
            "approved_tasks",
            []
        )
    )

    # =================================================
    # DON'T DUPLICATE APPROVAL
    # =================================================

    if task_id not in approved_tasks:

        approved_tasks.append(
            task_id
        )

    return {

        "approved_tasks":
            approved_tasks,

        "pending_approval":
            None,

        "execution_complete":
            False,
    }


# =====================================================
# ROUTING AFTER EXECUTOR
# =====================================================

def route_after_executor(
    state
):

    # =================================================
    # APPROVAL REQUIRED
    # =================================================

    if state.get(
        "pending_approval"
    ):

        return "approval"

    # =================================================
    # EVERYTHING COMPLETED
    # =================================================

    if state.get(
        "execution_complete"
    ):

        return "chatbot"

    # =================================================
    # MORE TASKS
    # =================================================

    return "execute_tasks"


# =====================================================
# ROUTING AFTER APPROVAL
# =====================================================

def route_after_approval(
    state
):

    # =================================================
    # REJECTED
    # =================================================

    if state.get(
        "execution_complete"
    ):

        return "chatbot"

    # =================================================
    # APPROVED
    # =================================================

    return "execute_tasks"


# =====================================================
# CREATE GRAPH
# =====================================================

def create_graph(
    tools,
    memory,
):

    builder = StateGraph(
        AgentState
    )

    # =================================================
    # NODES
    # =================================================

    builder.add_node(
        "supervisor",
        supervisor
    )

    builder.add_node(
        "execute_tasks",
        execute_tasks
    )

    builder.add_node(
        "approval",
        approval_node
    )

    builder.add_node(
        "chatbot",
        chatbot
    )

    # =================================================
    # START → SUPERVISOR
    # =================================================

    builder.add_edge(
        START,
        "supervisor"
    )

    # =================================================
    # SUPERVISOR → EXECUTOR
    # =================================================

    builder.add_edge(
        "supervisor",
        "execute_tasks"
    )

    # =================================================
    # EXECUTOR → ROUTING
    # =================================================

    builder.add_conditional_edges(

        "execute_tasks",

        route_after_executor,

        {
            "approval":
                "approval",

            "execute_tasks":
                "execute_tasks",

            "chatbot":
                "chatbot",
        },
    )

    # =================================================
    # APPROVAL → ROUTING
    # =================================================

    builder.add_conditional_edges(

        "approval",

        route_after_approval,

        {
            "execute_tasks":
                "execute_tasks",

            "chatbot":
                "chatbot",
        },
    )

    # =================================================
    # CHATBOT → END
    # =================================================

    builder.add_edge(
        "chatbot",
        END
    )

    # =================================================
    # COMPILE
    # =================================================

    return builder.compile(
        checkpointer=memory
    )