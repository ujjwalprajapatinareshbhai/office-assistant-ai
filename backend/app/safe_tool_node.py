from langgraph.types import interrupt

from app.risk import check_tool_risk

from langchain_core.messages import (
    ToolMessage,
    HumanMessage,
)


class SafeToolNode:

    def __init__(self, tools):

        self.tools = tools

        self.tool_map = {
            tool.name: tool
            for tool in tools
        }

    async def __call__(
        self,
        state,
        config,
    ):

        messages = state["messages"]

        last_message = messages[-1]

        tool_calls = getattr(
            last_message,
            "tool_calls",
            []
        )

        if not tool_calls:
            return {}

        user_request = ""

        for message in reversed(messages):

            if isinstance(message, HumanMessage):

                user_request = message.content
                break

        results = []

        for tool_call in tool_calls:

            tool_name = tool_call["name"]

            arguments = tool_call.get(
                "args",
                {}
            )

            tool_call_id = tool_call["id"]

            tool = self.tool_map.get(
                tool_name
            )

            if tool is None:

                raise ValueError(
                    f"Tool '{tool_name}' not found."
                )

            description = (
                tool.description
                or ""
            )

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

            if risk_result["requires_approval"]:

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
                        "\n❌ Tool execution cancelled."
                    )

                    results.append(
                        ToolMessage(
                            content=(
                                "Tool execution was cancelled "
                                "because human approval was not granted."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    )

                    continue

                print(
                    "\n✅ Approved. Continuing..."
                )

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

                results.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call_id,
                    )
                )

            except Exception as e:

                print(
                    f"\n❌ Tool execution failed: "
                    f"{tool_name}"
                )

                print(
                    f"Reason: {e}"
                )

                results.append(
                    ToolMessage(
                        content=(
                            f"Tool execution failed: {str(e)}"
                        ),
                        tool_call_id=tool_call_id,
                    )
                )

        return {
            "messages": results
        }