
import asyncio

from langgraph.types import interrupt

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.memory_retriever import build_memory_context

from app.guardrails import output_guardrail
from app.agent import build_prompt_messages

from guardrails.errors import ValidationError
from app.guardrails_ai import safe_response_guard


async def chatbot(state, config):

    llm = config["configurable"]["llm"]

    thread_id = config["configurable"]["thread_id"]

    messages = state["messages"]

    # =================================================
    # GET EXECUTED TASK RESULTS
    # =================================================

    task_results = state.get(
        "task_results",
        {}
    )

    # =================================================
    # FIND LAST USER MESSAGE
    # =================================================

    last_user_message = None

    for message in reversed(messages):

        if isinstance(message, HumanMessage):

            last_user_message = message.content

            break

    # =================================================
    # LONG-TERM MEMORY
    # =================================================

    memory_context = build_memory_context(
        thread_id
    )

    # =================================================
    # SYSTEM PROMPT
    # =================================================

    system_prompt = f"""
You are an intelligent office assistant.

You have access to:

1. Long-term user memories.
2. Company documents retrieved using RAG.
3. Results from MCP tools already executed
   by the application.

Your job is to provide the final answer to the user.

--------------------------------------------------
IMPORTANT TOOL EXECUTION RULE
--------------------------------------------------

The application is responsible for executing tools.

If EXECUTED TASK RESULTS are present below:

- The tools have ALREADY been executed.
- Do NOT call another tool.
- Do NOT repeat the tool execution.
- Do NOT ask the user for confirmation.
- Use the results directly to answer the user.

The application handles:

- tool selection
- execution planning
- parallel execution
- risk analysis
- human approval
- MCP communication
- RAG retrieval
- file retrieval

You only need to explain the final results.

--------------------------------------------------
GENERAL INSTRUCTIONS
--------------------------------------------------

- Use stored memories whenever they help answer
  personal questions.

- Use retrieved company documents whenever they
  contain useful information.

- Use executed task results when answering requests
  involving tools.

- Do not invent information.

- If a task failed, clearly explain that it failed.

- If multiple tasks were executed, combine their
  results into one clear response.

- Never claim a tool was executed if there is no
  corresponding result.

--------------------------------------------------
STORED USER MEMORIES
--------------------------------------------------

{memory_context}

--------------------------------------------------
EXECUTED TASK RESULTS
--------------------------------------------------

{task_results}

The tools have already been executed.

Do NOT call another tool.

Use the task results above to answer
the user's request directly.
"""

    # =================================================
    # BUILD FINAL MESSAGES
    # =================================================

    final_messages = [

        SystemMessage(
            content=system_prompt
        ),

        *messages,
    ]

    # =================================================
    # CALL LLM
    # =================================================

    response = await llm.ainvoke(
        final_messages
    )

    # =================================================
    # IMPORTANT
    # =================================================
    #
    # In the new architecture, the executor handles
    # MCP tool execution.
    #
    # Therefore, if task_results exist, this response
    # should be treated as the final user-facing answer.
    #
    # We do not send tool calls back into SafeToolNode.
    # =================================================

    if response.tool_calls:

        print(
            "\n⚠️ Chatbot attempted an additional "
            "tool call after task execution."
        )

        response.content = (
            "I have already executed the requested "
            "operations. I cannot execute additional "
            "tools during the final response."
        )

    # =================================================
    # FINAL USER-FACING RESPONSE
    # =================================================

    response_text = response.content

    # =================================================
    # EXISTING OUTPUT GUARDRAIL
    # =================================================

    if not await output_guardrail(
        response_text
    ):

        print(
            "\n⚠️ OUTPUT GUARDRAIL: "
            "Response blocked."
        )

        response.content = (
            "I'm sorry, but I can't provide "
            "that response."
        )

    else:

        # =================================================
        # GUARDRAILS AI
        # =================================================

        try:

            # Guardrails validation is synchronous.
            #
            # Run it in a worker thread so it does
            # not block the async LangGraph event loop.

            validation_result = await asyncio.to_thread(
                safe_response_guard.validate,
                response_text
            )

            if not validation_result.validation_passed:

                print(
                    "\n🛡️ GUARDRAILS AI: "
                    "Response blocked."
                )

                response.content = (
                    "I'm sorry, but I can't provide "
                    "that response."
                )

            else:

                print(
                    "\n🛡️ GUARDRAILS AI: "
                    "Response passed."
                )

        except ValidationError as e:

            print(
                "\n🛡️ GUARDRAILS AI: "
                "Response blocked."
            )

            print(
                f"Reason: {e}"
            )

            response.content = (
                "I'm sorry, but I can't provide "
                "that response."
            )

        except Exception as e:

            print(
                "\n⚠️ Guardrails AI error:"
            )

            print(
                f"Reason: {e}"
            )

            response.content = (
                "I'm sorry, but I can't provide "
                "that response."
            )

    # =================================================
    # RETURN RESPONSE
    # =================================================

    return {
        "messages": [response]
    }


# =====================================================
# RISK CHECK
# =====================================================

async def risk_check(state, config):

    messages = state["messages"]

    last_message = messages[-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        []
    )

    if not tool_calls:

        return {}

    llm = config["configurable"]["llm"]

    for tool_call in tool_calls:

        tool_name = tool_call["name"]

        arguments = tool_call.get(
            "args",
            {}
        )

        # =================================================
        # RISK ANALYSIS PROMPT
        # =================================================

        prompt = f"""
You are a security and authorization evaluator.

A user asked an AI agent to perform a tool operation.

Tool name:
{tool_name}

Arguments:
{arguments}

Determine whether executing this operation requires
human approval.

HIGH RISK means the operation could:

- delete or permanently remove data
- send something externally
- cause financial consequences
- change important records
- expose sensitive information
- cause an irreversible action
- create significant real-world consequences

LOW RISK means the operation is:

- read-only
- searching
- calculating
- retrieving information
- checking status
- another harmless operation

MEDIUM RISK means it changes data but has relatively
limited consequences.

Return ONLY one word:

HIGH
MEDIUM
LOW
"""

        # =================================================
        # ASK LLM FOR RISK
        # =================================================

        # result = await llm.ainvoke(
        #     [
        #         SystemMessage(
        #             content=prompt
        #         )
        #     ]
        # )
        result = await llm.ainvoke(
            build_prompt_messages(prompt)
        )

        risk = (
            result.content
            .strip()
            .upper()
        )

        print(
            f"\n🔍 AI Risk Decision: "
            f"{tool_name} → {risk}"
        )

        # =================================================
        # HIGH RISK → HUMAN APPROVAL
        # =================================================

        if risk == "HIGH":

            approval = interrupt(
                {
                    "type": "human_approval",
                    "tool": tool_name,
                    "arguments": arguments,
                    "risk": risk,
                    "message": (
                        f"The AI classified "
                        f"'{tool_name}' as HIGH risk."
                    ),
                }
            )

            if approval not in (
                "yes",
                "y",
                "approve",
                "approved",
                True,
            ):

                raise RuntimeError(
                    "Human approval was not granted."
                )

    return {}

