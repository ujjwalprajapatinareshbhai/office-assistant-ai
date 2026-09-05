import asyncio
from typing import Any

from langchain_core.messages import HumanMessage

from app.risk import check_tool_risk
from langchain_core.messages import ToolMessage


class ParallelToolExecutor:

    def __init__(self, tools):

        self.tools = tools

        self.tool_map = {
            tool.name: tool
            for tool in tools
        }

    # =================================================
    # GET ORIGINAL USER REQUEST
    # =================================================

    def get_user_request(self, messages):

        for message in reversed(messages):

            if isinstance(message, HumanMessage):

                return message.content

        return ""

    # =================================================
    # CHECK WHETHER TASK IS READY
    # =================================================

    def is_ready(
        self,
        task,
        completed_tasks,
    ):

        dependencies = task.get(
            "depends_on",
            []
        )

        return all(
            dependency in completed_tasks
            for dependency in dependencies
        )

    # =================================================
    # RESOLVE TASK ARGUMENTS
    # =================================================

    def resolve_arguments(
        self,
        arguments,
        task_results,
    ):

        if not isinstance(arguments, dict):

            return arguments

        resolved = {}

        for key, value in arguments.items():

            if (
                isinstance(value, str)
                and value.startswith(
                    "{{FROM_TASK:"
                )
                and value.endswith(
                    "}}"
                )
            ):

                task_id = value[
                    len("{{FROM_TASK:"):-2
                ]

                resolved[key] = task_results.get(
                    task_id,
                    ""
                )

            else:

                resolved[key] = value

        return resolved

    # =================================================
    # EXECUTE ONE TASK
    # =================================================

    async def execute_task(
        self,
        task,
        user_request,
        task_results,
        config,
    ):

        task_id = task["id"]

        tool_name = task["tool"]

        arguments = self.resolve_arguments(
            task.get(
                "arguments",
                {}
            ),
            task_results,
        )

        tool = self.tool_map.get(
            tool_name
        )

        if tool is None:

            return (
                task_id,
                {
                    "success": False,
                    "error": (
                        f"Tool '{tool_name}' "
                        f"not found."
                    ),
                }
            )

        description = (
            tool.description
            or ""
        )

        # =================================================
        # RISK ANALYSIS
        # =================================================

        risk_result = await check_tool_risk(
            user_request=user_request,
            tool_name=tool_name,
            tool_description=description,
            arguments=arguments,
        )

        print(
            f"\n🔍 Risk Analysis: "
            f"{risk_result['risk']}"
        )

        print(
            f"Reason: "
            f"{risk_result['reason']}"
        )

        # =================================================
        # HUMAN APPROVAL
        # =================================================

        if risk_result["requires_approval"]:

            from langgraph.types import interrupt

            approval = interrupt(
                {
                    "type": "tool_approval",
                    "tool": tool_name,
                    "arguments": arguments,
                    "risk": risk_result["risk"],
                    "reason": risk_result["reason"],
                }
            )

            if (
                not approval
                or str(approval).lower()
                not in {
                    "yes",
                    "y",
                    "approve",
                    "approved",
                }
            ):

                print(
                    f"\n❌ Task cancelled: "
                    f"{task_id}"
                )

                return (
                    task_id,
                    {
                        "success": False,
                        "cancelled": True,
                        "result": (
                            "Tool execution was "
                            "cancelled because "
                            "human approval was "
                            "not granted."
                        ),
                    }
                )

            print(
                "\n✅ Approved. Continuing..."
            )

        # =================================================
        # EXECUTE TOOL
        # =================================================

        print(
            f"\n🔧 Running tool: "
            f"{tool_name}"
        )

        try:

            result = await tool.ainvoke(
                arguments
            )

            print(
                f"✅ Finished tool: "
                f"{tool_name}"
            )

            return (
                task_id,
                {
                    "success": True,
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": str(result),
                }
            )

        except Exception as e:

            print(
                f"\n❌ Tool execution failed: "
                f"{tool_name}"
            )

            print(
                f"Reason: {e}"
            )

            return (
                task_id,
                {
                    "success": False,
                    "tool": tool_name,
                    "arguments": arguments,
                    "error": str(e),
                }
            )

    # =================================================
    # MAIN EXECUTOR
    # =================================================

    async def __call__(
        self,
        state,
        config,
    ):

        execution_plan = state.get(
            "execution_plan",
            []
        )

        task_results = dict(
            state.get(
                "task_results",
                {}
            )
        )

        completed_tasks = list(
            state.get(
                "completed_tasks",
                []
            )
        )

        messages = state["messages"]

        user_request = self.get_user_request(
            messages
        )

        # =================================================
        # FIND READY TASKS
        # =================================================

        ready_tasks = []

        for task in execution_plan:

            task_id = task["id"]

            # Already completed
            if task_id in completed_tasks:
                continue

            # Dependencies not finished
            if not self.is_ready(
                task,
                completed_tasks,
            ):
                continue

            ready_tasks.append(task)

        # =================================================
        # NOTHING TO EXECUTE
        # =================================================

        if not ready_tasks:

            return {
                "task_results": task_results,
                "completed_tasks": completed_tasks,
                "active_tasks": [],
            }

        # =================================================
        # DISPLAY PARALLEL TASKS
        # =================================================

        print(
            "\n⚡ PARALLEL EXECUTION"
        )

        print(
            f"Running {len(ready_tasks)} "
            f"independent task(s)..."
        )

        for task in ready_tasks:

            print(
                f"  → {task['id']} : "
                f"{task['tool']}"
            )

        # =================================================
        # RUN TASKS CONCURRENTLY
        # =================================================

        results = await asyncio.gather(
            *[
                self.execute_task(
                    task=task,
                    user_request=user_request,
                    task_results=task_results,
                    config=config,
                )
                for task in ready_tasks
            ]
        )

        # =================================================
        # STORE RESULTS
        # =================================================

        new_completed_tasks = list(
            completed_tasks
        )

        for task_id, result in results:

            task_results[task_id] = result

            if task_id not in new_completed_tasks:

                new_completed_tasks.append(
                    task_id
                )

        # =================================================
        # RETURN
        # =================================================

        return {
            "task_results": task_results,
            "completed_tasks": new_completed_tasks,
            "active_tasks": [],
        }
        