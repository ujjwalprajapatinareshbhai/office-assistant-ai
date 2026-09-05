import asyncio
import uuid

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.agent import llm
from app.graph import create_graph
from app.memory import create_memory
from app.memory_extractor import remember
from app.tools import load_tools

from app.guardrails import (
    input_guardrail,
    detect_prompt_injection,
)


# ==================================================
# STREAM CHATBOT OUTPUT
# ==================================================

async def stream_chatbot(
    graph,
    input_data,
    config,
):

    async for event in graph.astream_events(
        input_data,
        config=config,
        version="v2",
    ):

        event_type = event[
            "event"
        ]

        # ==================================================
        # ONLY STREAM CHATBOT
        # ==================================================

        if event_type != "on_chat_model_stream":
            continue

        metadata = event.get(
            "metadata",
            {}
        )

        if (
            metadata.get(
                "langgraph_node"
            )
            != "chatbot"
        ):
            continue

        chunk = (
            event["data"]["chunk"]
            .content
        )

        if not chunk:
            continue

        # ==================================================
        # IGNORE INTERNAL GUARDRAIL OUTPUT
        # ==================================================

        if chunk.strip().upper() in {
            "SAFE",
            "BLOCK",
        }:
            continue

        print(
            chunk,
            end="",
            flush=True,
        )

    print()


# ==================================================
# DISPLAY APPROVAL REQUEST
# ==================================================

def display_approval(
    interrupt_value,
):

    print(
        "\n" + "=" * 60
    )

    print(
        "⚠️ HUMAN APPROVAL REQUIRED"
    )

    print(
        "=" * 60
    )

    print(
        "Tool:",
        interrupt_value.get(
            "tool",
            "Unknown",
        ),
    )

    print(
        "Arguments:",
        interrupt_value.get(
            "arguments",
            {},
        ),
    )

    print(
        "\nRisk:",
        interrupt_value.get(
            "risk",
            "Unknown",
        ),
    )

    print(
        "Reason:",
        interrupt_value.get(
            "reason",
            "No reason",
        ),
    )

    print(
        "\nMessage:",
        interrupt_value.get(
            "message",
            "",
        ),
    )

    print(
        "=" * 60
    )


# ==================================================
# MAIN
# ==================================================

async def main():

    # --------------------------------------------------
    # LOAD TOOLS
    # --------------------------------------------------

    tools = await load_tools()

    print(
        f"Loaded {len(tools)} tools."
    )

    llm_with_tools = llm.bind_tools(
        tools
    )

    # --------------------------------------------------
    # CREATE CHECKPOINTER
    # --------------------------------------------------

    async with create_memory() as memory:

        graph = create_graph(
            tools=tools,
            memory=memory,
        )

        thread_id = str(
            uuid.uuid4()
        )

        config = {
            "configurable": {
                "thread_id": thread_id,
                "llm": llm_with_tools,
                "tools": tools,
            }
        }

        # ==================================================
        # CHAT LOOP
        # ==================================================

        while True:

            question = input(
                "\nYou: "
            ).strip()

            if question.lower() == "exit":
                break

            # ==================================================
            # INPUT GUARDRAIL
            # ==================================================

            allowed = await input_guardrail(
                question
            )

            if not allowed:

                print(
                    "\n🛑 INPUT GUARDRAIL: "
                    "Request blocked."
                )

                continue

            # ==================================================
            # PROMPT INJECTION DETECTION
            # ==================================================

            safe = await detect_prompt_injection(
                question
            )

            if not safe:

                print(
                    "\n🛡️ PROMPT INJECTION GUARDRAIL: "
                    "Attack detected."
                )

                continue

            # ==================================================
            # SAVE LONG-TERM MEMORY
            # ==================================================

            await remember(
                thread_id,
                question,
            )

            print()

            # ==================================================
            # START GRAPH
            # ==================================================

            await stream_chatbot(
                graph,
                {
                    "messages": [
                        HumanMessage(
                            content=question
                        )
                    ]
                },
                config,
            )

            # ==================================================
            # CHECK GRAPH STATE
            # ==================================================

            state = await graph.aget_state(
                config
            )

            # ==================================================
            # NO INTERRUPT
            # ==================================================

            if not state.tasks:

                continue

            # ==================================================
            # PROCESS INTERRUPT
            # ==================================================

            approval_handled = False

            for task in state.tasks:

                if not task.interrupts:
                    continue

                # ==============================================
                # GET INTERRUPT DATA
                # ==============================================

                interrupt_value = (
                    task.interrupts[0].value
                )

                # ==============================================
                # DISPLAY ONCE
                # ==============================================

                display_approval(
                    interrupt_value
                )

                # ==============================================
                # ASK USER
                # ==============================================

                answer = input(
                    "\nApprove? (yes/no): "
                ).strip().lower()

                # ==============================================
                # REJECT
                # ==============================================

                if answer not in (
                    "yes",
                    "y",
                    "approve",
                    "approved",
                ):

                    print(
                        "\n❌ Tool execution cancelled."
                    )

                    # ==========================================
                    # RESUME WITH REJECTION
                    # ==========================================

                    await stream_chatbot(
                        graph,
                        Command(
                            resume="no"
                        ),
                        config,
                    )

                    approval_handled = True

                    break

                # ==============================================
                # APPROVE
                # ==============================================

                print(
                    "\n✅ Approved. Continuing...\n"
                )

                # ==============================================
                # RESUME GRAPH
                # ==============================================

                await stream_chatbot(
                    graph,
                    Command(
                        resume="yes"
                    ),
                    config,
                )

                approval_handled = True

                break

            # ==================================================
            # DONE
            # ==================================================

            if approval_handled:

                print()


# ==================================================
# APPLICATION ENTRY POINT
# ==================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )