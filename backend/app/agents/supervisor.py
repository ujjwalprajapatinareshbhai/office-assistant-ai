import asyncio
import json

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.schemas import SupervisorPlan
from app.agent import (
    get_structured_llm,
    call_structured_llm,
    build_prompt_messages,
    get_lean_tool_schema,
)


async def supervisor(
    state,
    config
):

    print(
        "\n=============================================="
    )

    print(
        "🧠 SUPERVISOR STARTED"
    )

    print(
        "=============================================="
    )

    # =================================================
    # GET LLM
    # =================================================

    configurable = config.get(
        "configurable",
        {}
    )

    llm = configurable.get(
        "llm"
    )

    if llm is None:

        print(
            "\n❌ Supervisor LLM is None."
        )

        return {
            "execution_plan": [],
            "routing_reason":
                "Supervisor LLM is not configured.",
            "next_agent": "",
            "active_tasks": [],
            "completed_tasks": [],
            "task_results": {},
        }

    print(
        "✅ Supervisor LLM loaded."
    )

    # =================================================
    # GET MESSAGES
    # =================================================

    messages = state.get(
        "messages",
        []
    )

    print(
        f"📨 Messages available: {len(messages)}"
    )

    # =================================================
    # GET USER REQUEST
    # =================================================

    user_request = ""

    for message in reversed(messages):

        if isinstance(
            message,
            HumanMessage
        ):

            user_request = message.content

            break

    if not user_request:

        print(
            "\n⚠️ No user request found."
        )

        return {
            "execution_plan": [],
            "routing_reason":
                "No user request was found.",
            "next_agent": "",
            "active_tasks": [],
            "completed_tasks": [],
            "task_results": {},
        }

    print(
        "\n👤 USER REQUEST:"
    )

    print(
        user_request
    )

    # =================================================
    # GET MCP TOOLS
    # =================================================

    tools = configurable.get(
        "tools",
        []
    )

    print(
        f"\n🔧 Available MCP tools: {len(tools)}"
    )

    # =================================================
    # BUILD TOOL CATALOG
    # =================================================

    tool_catalog = []

    for tool in tools:

        tool_catalog.append(
            {
                "name": tool.name,
                "description": tool.description or "",
                "arguments": get_lean_tool_schema(tool),
            }
        )

    tool_catalog_text = json.dumps(
        tool_catalog,
        indent=2,
        default=str
    )

    # =================================================
    # SUPERVISOR PROMPT
    # =================================================

    prompt = f"""
You are the supervisor of an AI office assistant.

Your job is to understand the user's CURRENT request
and create ONLY the execution plan required for that
request.

You DO NOT execute tools.

You ONLY create the execution plan.

The application will execute the tools later.

==================================================
AVAILABLE MCP TOOLS
==================================================

{tool_catalog_text}

==================================================
CURRENT USER REQUEST
==================================================

{user_request}

==================================================
GENERAL PLANNING RULES
==================================================

1. Use ONLY tools that actually exist in the
   AVAILABLE MCP TOOLS list.

2. Never invent a tool.

3. Understand the user's CURRENT request first.

4. Create ONLY the tasks necessary to satisfy the
   CURRENT request.

5. Do NOT create unrelated tasks.

6. Do NOT execute any tool.

7. Independent tasks should have no dependencies.

8. Dependent tasks MUST specify depends_on.

9. A dependent task MUST NOT run before all of its
   dependencies have completed.

10. Always follow the EXACT argument schema of the
    selected MCP tool.

11. NEVER guess the type of a tool argument.

12. A string argument MUST contain a string.

13. An integer argument MUST contain an integer.

14. A number argument MUST contain a number.

15. A boolean argument MUST contain true or false.

16. An array argument MUST contain an array.

17. An object argument MUST contain an object.

18. NEVER use [] as a placeholder for a string.

19. NEVER use {{}} as a placeholder for a required
    argument.

20. NEVER use an empty string for an unknown required
    argument.

21. NEVER invent filenames.

22. NEVER invent employee information.

23. NEVER invent email addresses.

24. NEVER invent tool arguments.

25. If required information is unknown, create a
    dependency that obtains that information first.

==================================================
KNOWLEDGE BASE / RAG RULES
==================================================

The tool:

search_knowledge_base

searches the company's semantic knowledge base
using vector retrieval.

Use search_knowledge_base when the user asks about
information contained in company knowledge documents,
policies, procedures, employee handbook information,
internal company information, or other indexed
knowledge.

Examples:

User:

"What is the leave policy?"

Correct:

{{
    "id": "task_1",
    "tool": "search_knowledge_base",
    "arguments": {{
        "query": "leave policy"
    }},
    "depends_on": []
}}

User:

"How many paid leaves do employees get?"

Correct:

{{
    "id": "task_1",
    "tool": "search_knowledge_base",
    "arguments": {{
        "query": "paid leave policy"
    }},
    "depends_on": []
}}

User:

"What are the company working hours?"

Correct:

{{
    "id": "task_1",
    "tool": "search_knowledge_base",
    "arguments": {{
        "query": "company working hours"
    }},
    "depends_on": []
}}

Do NOT use web search for internal company knowledge.

Do NOT use employee tools unless the user asks
about an employee.

Do NOT use search_files_content when semantic
company knowledge retrieval is sufficient.

Use search_knowledge_base for knowledge questions.

Use search_files_content when the user specifically
needs to locate a file or when file-name/content
search is required.

Use get_file when the actual file contents are
required.

==================================================
FILE / DOCUMENT RULES
==================================================

IMPORTANT:

There are TWO different document systems.

--------------------------------------------------
1. KNOWLEDGE BASE / RAG
--------------------------------------------------

Use:

search_knowledge_base

when the user wants INFORMATION FROM document
content.

This includes:

- company policies
- leave policies
- HR information
- employee handbook information
- company procedures
- information contained in indexed documents
- information contained in an uploaded PDF
- information contained in an uploaded document
- summaries or explanations of document content
- questions asking "what does the document say?"

Examples:

"What is the leave policy?"

"What are the company working hours?"

"According to the company policy, can employees work from home?"

"What are the main impacts mentioned in this document?"

"Summarize this document."

For these requests, use:

search_knowledge_base

Do NOT use search_files_content merely because the
question mentions a document, policy, PDF, or file.

--------------------------------------------------
2. STATIC COMPANY FILE SYSTEM
--------------------------------------------------

Use:

search_files_content

when the user wants to FIND or LOCATE a file in the
static company file system.

Examples:

"Find the leave policy document."

"Find the document containing the leave policy."

"Do we have a leave policy document?"

"Find leave_policy.txt."

Use:

search_files_content

for these requests.

--------------------------------------------------
EXACT FILENAME
--------------------------------------------------

If the user explicitly provides the exact filename and
wants the actual contents of that file:

Use get_file directly.

Example:

User:

"Read leave_policy.txt"

Correct:

{{
    "id": "task_1",
    "tool": "get_file",
    "arguments": {{
        "file_name": "leave_policy.txt"
    }},
    "depends_on": []
}}

Do NOT search for the file first when the exact
filename is explicitly provided.

--------------------------------------------------
UNKNOWN FILENAME + STATIC FILE REQUEST
--------------------------------------------------

If the user wants to LOCATE a static file but does not
provide its exact filename:

First use:

search_files_content

Example:

User:

"Find the document containing the leave policy."

Correct:

{{
    "id": "task_1",
    "tool": "search_files_content",
    "arguments": {{
        "keyword": "leave policy"
    }},
    "depends_on": []
}}

--------------------------------------------------
STATIC FILE CONTENT AFTER SEARCH
--------------------------------------------------

If the user wants the actual contents of a static
company file but the filename is unknown:

1. Use search_files_content.
2. Then use get_file.
3. get_file MUST depend on the search task.
4. get_file.file_name MUST use the result of the
   search task.
5. NEVER invent the filename.

Example:

User:

"Read the complete leave policy document."

ONLY use search_files_content + get_file when the
request refers to locating/reading a STATIC COMPANY
FILE.

Correct structure:

{{
    "id": "task_1",
    "tool": "search_files_content",
    "arguments": {{
        "keyword": "leave policy"
    }},
    "depends_on": []
}}

{{
    "id": "task_2",
    "tool": "get_file",
    "arguments": {{
        "file_name": "{{{{FROM_TASK:task_1}}}}"
    }},
    "depends_on": ["task_1"]
}}

--------------------------------------------------
CRITICAL DISTINCTION
--------------------------------------------------

If the user asks:

"What is the leave policy?"

Use:

search_knowledge_base

NOT:

search_files_content

If the user asks:

"Find the leave policy document."

Use:

search_files_content

If the user asks:

"Read leave_policy.txt."

Use:

get_file

If the user asks:

"What does the uploaded PDF say?"

Use:

search_knowledge_base

If the user asks:

"Summarize the uploaded document."

Use:

search_knowledge_base

If the user asks:

"According to the uploaded PDF, what are the main
impacts of generative AI?"

Use:

search_knowledge_base

==================================================
IMPORTANT FILE DEPENDENCY RULE
==================================================

When get_file depends on search_files_content:

The search result contains file metadata such as:

{{
    "file_name": "leave_policy.txt",
    "match_type": "content"
}}

Therefore the downstream get_file task must obtain the
actual file_name from the previous task result.

Use:

"file_name": "{{{{FROM_TASK:task_1}}}}"

Do NOT use:

"file_name": []

Do NOT use:

"file_name": {{}}

Do NOT use:

"file_name": ""

Do NOT invent:

"file_name": "leave_policy.txt"

unless the user explicitly provided that exact filename.

==================================================
MULTIPLE SEARCH RESULTS
==================================================

If search_files_content may return multiple matching
files, the supervisor MUST NOT invent which filename
is correct.

If the user only wants to locate the files,
search_files_content may be sufficient.

If the user wants the contents of a specific static
file and multiple files may match, the plan must not
pretend that the search result identifies a single
filename.

The system should only pass a filename to get_file
when the required file can be unambiguously determined.

==================================================
FROM_TASK RULE
==================================================

When a value genuinely comes from another task, use:

"{{FROM_TASK:task_id}}"

Example:

{{
    "file_name": "{{FROM_TASK:task_1}}"
}}

The referenced task must exist.

A FROM_TASK reference MUST always point to a task that
appears earlier in the execution dependency chain.

Never create a FROM_TASK reference to a nonexistent task.

==================================================
EMPLOYEE RULES
==================================================

If the user provides an employee ID, use that ID
directly.

Example:

User:

"Get employee 8 details."

Use:

{{
    "employee_id": 8
}}

Do not create unnecessary dependencies.

If the employee ID is NOT provided and the selected
employee tool requires an employee ID, obtain the
required employee information first using an available
tool that can actually provide it.

Never invent an employee ID.

==================================================
WEATHER RULES
==================================================

If the user provides a city, use that city directly.

Example:

User:

"Get today's weather for Valsad."

Use:

{{
    "city": "Valsad"
}}

Do not create unnecessary dependencies.

If the city is not provided and the weather tool requires
a city, do not invent a city.

==================================================
UPLOADED FILE / RAG RULES
==================================================
 
IMPORTANT: This is DIFFERENT from the static company
file system (get_file, search_files_content).
 
A separate tool, search_knowledge_base, searches
documents the user has UPLOADED during this
conversation (PDFs, TXT, DOCX, images/OCR), which are
embedded and stored specifically for this thread. It
also covers the permanent company knowledge base.
 
Use search_knowledge_base — NOT get_file,
get_file_list, or search_files_content — whenever the
user's request refers to:
 
- "the uploaded file"
- "the file I uploaded"
- "this PDF" / "this document"
- "the attached file"
- "analyze the uploaded file"
- any request that sounds like it's about content the
  user just attached/uploaded, rather than a named
  file that already exists in the company file system
 
Example:
 
User:
 
"Please analyze the uploaded file."
 
Correct plan:
 
reason:
 
"The user wants an analysis of a file they uploaded
to this conversation. Search the knowledge base for
its content."
 
tasks:
 
[
    {{
        "id": "task_1",
        "tool": "search_knowledge_base",
        "arguments": {{
            "query": "summary overview of the uploaded document"
        }},
        "depends_on": []
    }}
]
 
Do NOT use get_file_list or get_file for this kind of
request — those tools only see the static company
file system, not documents the user uploaded in this
conversation.
 
If the user's message ALSO gives specific instructions
(e.g. "list the coverage limits in the uploaded
policy"), use those instructions as the search
query instead of a generic summary request.
 
Do not create unnecessary dependencies.

==================================================
WEB SEARCH RULES
==================================================

If the user asks for:

- research
- current information
- future trends
- articles
- web information
- online information
- latest information

use the available web search tool.

Only create this task if the user actually asks for
web/research information.

Do NOT add web search to normal office-file questions
unless the user explicitly requests web information.

==================================================
REPORT RULES
==================================================

Only create a report task if the user asks for:

- a report
- a summary report
- a compilation
- a generated document
- a formal summary
- a consolidated report
- similar generated output

Do NOT create a report for a simple question.

If a report depends on multiple information sources:

1. Retrieve the required sources.

2. Create the report only after those sources are
   complete.

3. The report MUST depend on all required tasks.

Example:

task_1 -> employee information

task_2 -> weather information

task_3 -> report

task_3 depends_on:

[
    "task_1",
    "task_2"
]

==================================================
EMAIL RULES
==================================================

Only create an email task if the user asks to:

- send
- email
- forward
- communicate

If the user asks to email a result:

1. Retrieve the required information first.

2. Create the required email content.

3. The email task must depend on the task that produces
   the required information.

4. Use ONLY the argument names defined in the
   AVAILABLE MCP TOOLS schema.

5. NEVER invent email argument names such as:

   - recipient
   - email
   - email_address

6. If the send_a_email tool schema contains:

   - to
   - subject
   - body

   then use exactly:

   - to
   - subject
   - body

7. NEVER invent an email address.

8. Use the exact email address provided by the user.

9. If the recipient is not provided by the user and
   cannot be obtained from another task, do not invent one.

10. If the email body requires information from a previous
    task, use a FROM_TASK dependency and make the email
    task depend on that task.

11. Sending an email is an external action and will require
    human approval during execution.

Example:

User:

"Find employee 8 and email his details to john@example.com."

Correct structure:

task_1 -> employee lookup

task_2 -> send email

task_2 depends_on ["task_1"]

==================================================
MULTIPLE OPERATIONS
==================================================

When the user asks multiple things, split them into
necessary tasks.

Example:

"Get employee 8 details and today's weather for Valsad."

Create:

task_1 -> employee lookup

depends_on []

task_2 -> weather lookup

depends_on []

These can run in parallel.

If the user additionally asks:

"Create a report from both."

Create:

task_3 -> report

depends_on ["task_1", "task_2"]

==================================================
TASK DEPENDENCY RULES
==================================================

Use depends_on to represent execution dependencies.

A task should depend on another task ONLY when it
actually requires the result of that task.

Do NOT add dependencies merely because one task appears
before another.

Example:

Employee lookup and weather lookup are independent:

task_1:
depends_on []

task_2:
depends_on []

A report using both is dependent:

task_3:
depends_on ["task_1", "task_2"]

An email using the report is dependent:

task_4:
depends_on ["task_3"]

==================================================
NO UNRELATED TASKS
==================================================

For:

"What is the leave policy?"

Create ONLY the task required to answer the
leave-policy question.

Correct:

task_1 -> search_files_content

Do NOT create:

- employee tasks
- weather tasks
- web search tasks
- report tasks
- email tasks

unless explicitly requested.

For:

"What is the weather in Valsad?"

Create ONLY:

task_1 -> weather tool

Do NOT create:

- file tasks
- employee tasks
- email tasks
- report tasks
- web tasks

For:

"Get employee 8 details."

Create ONLY:

task_1 -> employee lookup

Do NOT create:

- file tasks
- weather tasks
- email tasks
- report tasks
- web tasks

==================================================
IMPORTANT FILE EXAMPLES
==================================================

Example 1:

User:

"What is the leave policy?"

Correct:

reason:

"Find the company leave policy."

tasks:

[
    {{
        "id": "task_1",
        "tool": "search_files_content",
        "arguments": {{
            "keyword": "leave policy"
        }},
        "depends_on": []
    }}
]

Do NOT automatically add get_file.

--------------------------------------------------

Example 2:

User:

"Read the complete leave policy."

Correct:

tasks:

[
    {{
        "id": "task_1",
        "tool": "search_files_content",
        "arguments": {{
            "keyword": "leave policy"
        }},
        "depends_on": []
    }},
    {{
        "id": "task_2",
        "tool": "get_file",
        "arguments": {{
            "file_name": "{{FROM_TASK:task_1}}"
        }},
        "depends_on": ["task_1"]
    }}
]

--------------------------------------------------

Example 3:

User:

"Read leave_policy.txt."

Correct:

tasks:

[
    {{
        "id": "task_1",
        "tool": "get_file",
        "arguments": {{
            "file_name": "leave_policy.txt"
        }},
        "depends_on": []
    }}
]

No search is necessary because the filename is known.

--------------------------------------------------

Example 4:

User:

"Find the document containing the leave policy."

Correct:

tasks:

[
    {{
        "id": "task_1",
        "tool": "search_files_content",
        "arguments": {{
            "keyword": "leave policy"
        }},
        "depends_on": []
    }}
]

Do NOT call get_file unless the user also asks for
the contents of the document.

==================================================
SEARCH_FILES_CONTENT BEHAVIOR
==================================================

The search_files_content tool searches:

1. File names
2. File contents

It returns matching files with metadata.

The result can look like:

[
    {{
        "file_name": "leave_policy.txt",
        "match_type": "content"
    }}
]

The file_name returned by search_files_content is the
value that should be supplied to get_file when the full
file must be retrieved.

Never invent that value.

==================================================
REPORT + FILE EXAMPLE
==================================================

User:

"Read the leave policy and create a report explaining it."

Correct:

task_1:
search_files_content

depends_on []

task_2:
get_file

depends_on ["task_1"]

task_3:
generate_report_tool

depends_on ["task_2"]

The report must NOT run before the file content has
been retrieved.

==================================================
FILE + EMAIL EXAMPLE
==================================================

User:

"Read the leave policy and email it to manager@example.com."

Correct structure:

task_1:
search_files_content

depends_on []

task_2:
get_file

depends_on ["task_1"]

task_3:
send_a_email

depends_on ["task_2"]

The email recipient must be exactly:

"manager@example.com"

Do not invent another recipient.

==================================================
MULTI-SOURCE EXAMPLE
==================================================

User:

"Get employee 8 details, check today's weather in Valsad,
and create a report combining both."

Correct:

task_1:

employee lookup

depends_on []

task_2:

weather lookup

depends_on []

task_3:

generate_report_tool

depends_on ["task_1", "task_2"]

The report must receive the information from both
previous tasks through FROM_TASK references.

==================================================
OUTPUT REQUIREMENTS
==================================================

Return a SupervisorPlan.

The SupervisorPlan must contain:

- reason
- tasks

Each task must contain:

- id
- tool
- arguments
- depends_on

The output MUST be valid structured data matching the
SupervisorPlan schema.

Do not return explanations outside the SupervisorPlan.

==================================================
FINAL VALIDATION
==================================================

Before returning the plan verify:

1. Every tool exists.

2. Every task is required by the CURRENT request.

3. No unrelated task was added.

4. Arguments are objects.

5. Required arguments are present.

6. Argument types match the tool schema.

7. String fields contain strings.

8. Number fields contain numbers.

9. Boolean fields contain booleans.

10. Array fields contain arrays.

11. No required string contains [].

12. No required string contains {{}}.

13. No required string is null.

14. No unknown filename is invented.

15. If the filename is unknown and file content is
    required, search_files_content MUST occur before
    get_file.

16. get_file MUST depend on the file-search task when
    the filename came from search_files_content.

17. get_file.file_name is either:

    - a known filename string explicitly provided by
      the user

    OR

    - "{{FROM_TASK:task_X}}"

18. Every FROM_TASK reference points to a real task.

19. Every dependent task contains the correct
    dependency.

20. Independent tasks do not unnecessarily depend
    on each other.

21. Do not create report/email tasks unless requested.

22. Do not create employee/weather/web/file tasks
    unless required by the user's request.

23. Do not create get_file automatically after every
    search_files_content task.

24. Use search_files_content alone when its search result
    is sufficient to answer the user's request.

25. Use get_file after search_files_content ONLY when
    the actual file content is required.

26. Never invent a filename to make get_file work.

27. When using FROM_TASK for file_name, the referenced
    task MUST be search_files_content.

28. When multiple tasks provide information to a report
    or email, the final task MUST depend on ALL required
    source tasks.

29. A task must never depend on a task whose result it
    does not actually need.

30. The execution plan must contain ONLY tasks required
    to satisfy the user's CURRENT request.
"""

    # =================================================
    # CALL STRUCTURED LLM
    # =================================================

    print(
        "\n=============================================="
    )

    print(
        "🧠 SUPERVISOR: CALLING STRUCTURED LLM"
    )

    print(
        "=============================================="
    )

    try:

        # =================================================
        # PROVIDER-AGNOSTIC STRUCTURED OUTPUT
        # =================================================
        #
        # get_structured_llm() automatically picks the
        # right method (json_schema for Ollama/Gemma,
        # native function-calling for OpenAI) based on
        # LLM_PROVIDER in .env. This file never needs to
        # know which provider is active.
        #
        # call_structured_llm() wraps the invoke with a
        # timeout AND a couple of retries, which self-heals
        # the Ollama cold-start "empty response" issue
        # without any special-casing here.
        # =================================================

        # ============ TEMPORARY DEBUG - remove after diagnosis ============
        print(f"\n🔬 DEBUG: Prompt length = {len(prompt)} characters")
        print(f"🔬 DEBUG: Approx tokens = {len(prompt) // 4}")  # rough estimate

        try:
            raw_response = await llm.ainvoke(build_prompt_messages(prompt))
            print(f"\n🔬 DEBUG RAW RESPONSE (provider-aware message):")
            print(f"Content length: {len(raw_response.content)}")
            print(f"Content: {repr(raw_response.content[:2000])}")
        except Exception as debug_e:
            print(f"🔬 DEBUG RAW CALL FAILED: {debug_e}")
        # ============ END TEMPORARY DEBUG ============

        structured_llm = get_structured_llm(
            llm,
            SupervisorPlan
        )

        response = await call_structured_llm(
            structured_llm,
            build_prompt_messages(prompt),
            timeout=120,
            retries=2,
        )

        print(
            "\n=============================================="
        )

        print(
            "✅ SUPERVISOR: STRUCTURED RESPONSE RECEIVED"
        )

        print(
            "=============================================="
        )

    except asyncio.TimeoutError:

        print(
            "\n=============================================="
        )

        print(
            "❌ SUPERVISOR LLM TIMEOUT"
        )

        print(
            "=============================================="
        )

        return {
            "execution_plan": [],
            "routing_reason":
                "Supervisor LLM timed out.",
            "next_agent": "",
            "active_tasks": [],
            "completed_tasks": [],
            "task_results": {},
        }

    except Exception as e:

        print(
            "\n=============================================="
        )

        print(
            "❌ SUPERVISOR STRUCTURED LLM ERROR"
        )

        print(
            "=============================================="
        )

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            repr(e)
        )

        import traceback

        traceback.print_exc()

        return {
            "execution_plan": [],
            "routing_reason":
                f"Supervisor structured LLM failed: {e}",
            "next_agent": "",
            "active_tasks": [],
            "completed_tasks": [],
            "task_results": {},
        }

    # =================================================
    # CONVERT PYDANTIC PLAN TO DICT
    # =================================================

    print(
        "\n========== SUPERVISOR STRUCTURED RESPONSE =========="
    )

    print(
        repr(response)
    )

    print(
        "====================================================="
    )

    try:

        # -------------------------------------------------
        # Pydantic v2
        # -------------------------------------------------

        if hasattr(
            response,
            "model_dump"
        ):

            result = response.model_dump()

        # -------------------------------------------------
        # Pydantic v1
        # -------------------------------------------------

        elif hasattr(
            response,
            "dict"
        ):

            result = response.dict()

        else:

            raise ValueError(
                "Supervisor response is not a valid "
                "SupervisorPlan object."
            )

    except Exception as e:

        print(
            "\n❌ Could not convert SupervisorPlan."
        )

        print(
            "Error:",
            repr(e)
        )

        return {
            "execution_plan": [],
            "routing_reason":
                "Supervisor returned an invalid "
                "structured plan.",
            "next_agent": "",
            "active_tasks": [],
            "completed_tasks": [],
            "task_results": {},
        }

    # =================================================
    # GET TASKS
    # =================================================

    tasks = result.get(
        "tasks",
        []
    )

    reason = result.get(
        "reason",
        "Execution plan created."
    )

    if not isinstance(
        tasks,
        list
    ):

        print(
            "\n❌ SupervisorPlan.tasks is not a list."
        )

        return {
            "execution_plan": [],
            "routing_reason":
                "Supervisor returned an invalid task list.",
            "next_agent": "",
            "active_tasks": [],
            "completed_tasks": [],
            "task_results": {},
        }

    print(
        "\n✅ Structured plan parsed successfully."
    )

    print(
        "Reason:",
        reason
    )

    print(
        "Tasks:",
        tasks
    )

    # =================================================
    # AVAILABLE TOOL NAMES
    # =================================================

    available_tool_names = {
        tool.name
        for tool in tools
    }

    # =================================================
    # VALIDATE TASKS
    # =================================================

    valid_tasks = []

    for task in tasks:

        # -------------------------------------------------
        # Convert Pydantic task to dict
        # -------------------------------------------------

        if hasattr(
            task,
            "model_dump"
        ):

            task = task.model_dump()

        elif hasattr(
            task,
            "dict"
        ):

            task = task.dict()

        if not isinstance(
            task,
            dict
        ):

            print(
                "\n⚠️ Ignoring invalid task."
            )

            continue

        # ---------------------------------------------
        # TOOL
        # ---------------------------------------------

        tool_name = task.get(
            "tool"
        )

        if not tool_name:

            print(
                "\n⚠️ Task has no tool."
            )

            continue

        # ---------------------------------------------
        # TOOL MUST EXIST
        # ---------------------------------------------

        if (
            tool_name
            not in available_tool_names
        ):

            print(
                f"\n⚠️ Unknown tool: {tool_name}"
            )

            continue

        # ---------------------------------------------
        # ARGUMENTS
        # ---------------------------------------------

        arguments = task.get(
            "arguments",
            {}
        )

        if not isinstance(
            arguments,
            dict
        ):

            print(
                f"\n⚠️ Invalid arguments for "
                f"{tool_name}: expected object."
            )

            continue

        # ---------------------------------------------
        # DEPENDENCIES
        # ---------------------------------------------

        depends_on = task.get(
            "depends_on",
            []
        )

        if depends_on is None:

            depends_on = []

        if not isinstance(
            depends_on,
            list
        ):

            print(
                f"\n⚠️ Invalid depends_on for "
                f"{tool_name}: expected list."
            )

            continue

        # ---------------------------------------------
        # TASK ID
        # ---------------------------------------------

        task_id = task.get(
            "id",
            f"task_{len(valid_tasks) + 1}"
        )

        valid_tasks.append(
            {
                "id": task_id,
                "tool": tool_name,
                "arguments": arguments,
                "depends_on": depends_on,
            }
        )

    # =================================================
    # VALIDATE DEPENDENCY REFERENCES
    # =================================================

    task_ids = {
        task["id"]
        for task in valid_tasks
    }

    cleaned_tasks = []

    for task in valid_tasks:

        valid_dependencies = []

        for dependency in task[
            "depends_on"
        ]:

            if dependency in task_ids:

                valid_dependencies.append(
                    dependency
                )

            else:

                print(
                    f"\n⚠️ Invalid dependency "
                    f"'{dependency}' in {task['id']}"
                )

        task[
            "depends_on"
        ] = valid_dependencies

        cleaned_tasks.append(
            task
        )

    valid_tasks = cleaned_tasks

    # =================================================
    # NORMALIZE FROM_TASK
    # =================================================

    for task in valid_tasks:

        arguments = task.get(
            "arguments",
            {}
        )

        for key, value in list(
            arguments.items()
        ):

            if not isinstance(
                value,
                str
            ):

                continue

            # Convert:
            #
            # {FROM_TASK:task_1}
            #
            # into:
            #
            # {{FROM_TASK:task_1}}

            if (
                value.startswith(
                    "{FROM_TASK:"
                )
                and value.endswith(
                    "}"
                )
                and not value.startswith(
                    "{{FROM_TASK:"
                )
            ):

                dependency_id = value[
                    len("{FROM_TASK:")
                    :
                    -1
                ]

                arguments[key] = (
                    "{{FROM_TASK:"
                    + dependency_id
                    + "}}"
                )

    # =================================================
    # STRICT FILE SAFETY VALIDATION
    # =================================================

    for task in list(
        valid_tasks
    ):

        if task[
            "tool"
        ] != "get_file":

            continue

        arguments = task.get(
            "arguments",
            {}
        )

        file_name = arguments.get(
            "file_name"
        )

        # ---------------------------------------------
        # MISSING FILE NAME
        # ---------------------------------------------

        if (
            file_name is None
            or file_name == ""
            or file_name == {}
            or file_name == []
        ):

            print(
                "\n❌ INVALID get_file ARGUMENT"
            )

            print(
                "get_file.file_name is missing."
            )

            print(
                "Removing unsafe get_file task."
            )

            valid_tasks.remove(
                task
            )

            reason = (
                "The file name was not safely "
                "resolved. File search must occur "
                "before reading the file."
            )

            continue

        # ---------------------------------------------
        # FILE NAME MUST BE STRING
        # ---------------------------------------------

        if not isinstance(
            file_name,
            str
        ):

            print(
                "\n❌ INVALID get_file ARGUMENT"
            )

            print(
                "get_file.file_name must be a string."
            )

            valid_tasks.remove(
                task
            )

            reason = (
                "The requested file could not be "
                "identified safely."
            )

            continue

        # ---------------------------------------------
        # FROM_TASK PLACEHOLDER
        # ---------------------------------------------

        if file_name.startswith(
            "{{FROM_TASK:"
        ):

            if not file_name.endswith(
                "}}"
            ):

                print(
                    "\n❌ INVALID FROM_TASK "
                    "PLACEHOLDER"
                )

                valid_tasks.remove(
                    task
                )

                reason = (
                    "Invalid file dependency "
                    "placeholder."
                )

                continue

            dependency_task_id = file_name[
                len("{{FROM_TASK:")
                :
                -2
            ]

            # -----------------------------------------
            # REFERENCED TASK MUST EXIST
            # -----------------------------------------

            current_task_ids = {
                t["id"]
                for t in valid_tasks
            }

            if (
                dependency_task_id
                not in current_task_ids
            ):

                print(
                    "\n❌ INVALID FILE DEPENDENCY"
                )

                print(
                    f"Referenced task "
                    f"{dependency_task_id} "
                    f"does not exist."
                )

                valid_tasks.remove(
                    task
                )

                reason = (
                    "The file dependency could "
                    "not be resolved safely."
                )

                continue

            dependency_task = next(
                (
                    t
                    for t in valid_tasks
                    if t["id"]
                    == dependency_task_id
                ),
                None
            )

            # -----------------------------------------
            # DEPENDENCY MUST BE FILE SEARCH
            # -----------------------------------------

            if (
                dependency_task is None
                or dependency_task[
                    "tool"
                ]
                not in (
                    "search_files_content",
                    "search_from_all_files"
                )
            ):

                print(
                    "\n❌ INVALID FILE DEPENDENCY"
                )

                print(
                    "get_file must depend on a "
                    "file-search task."
                )

                valid_tasks.remove(
                    task
                )

                reason = (
                    "get_file must receive a filename "
                    "from a file-search task."
                )

                continue

            # -----------------------------------------
            # GET_FILE MUST DEPEND ON SEARCH
            # -----------------------------------------

            if dependency_task_id not in task[
                "depends_on"
            ]:

                print(
                    "\n⚠️ Adding missing file "
                    "search dependency."
                )

                task[
                    "depends_on"
                ].append(
                    dependency_task_id
                )

    # =================================================
    # FINAL FILE DEPENDENCY CHECK
    # =================================================

    task_ids = {
        task["id"]
        for task in valid_tasks
    }

    for task in valid_tasks:

        if task[
            "tool"
        ] != "get_file":

            continue

        file_name = task[
            "arguments"
        ].get(
            "file_name"
        )

        if not isinstance(
            file_name,
            str
        ):

            continue

        if file_name.startswith(
            "{{FROM_TASK:"
        ):

            dependency_task_id = file_name[
                len("{{FROM_TASK:")
                :
                -2
            ]

            if (
                dependency_task_id
                not in task["depends_on"]
            ):

                if (
                    dependency_task_id
                    in task_ids
                ):

                    task[
                        "depends_on"
                    ].append(
                        dependency_task_id
                    )

    # =================================================
    # DISPLAY PLAN
    # =================================================

    print(
        "\n🧭 SUPERVISOR"
    )

    print(
        f"Reason: {reason}"
    )

    print(
        "\n📋 EXECUTION PLAN:"
    )

    if not valid_tasks:

        print(
            "  No executable tasks created."
        )

    for task in valid_tasks:

        dependencies = task[
            "depends_on"
        ]

        if dependencies:

            print(
                f"  {task['id']} → "
                f"{task['tool']} "
                f"(depends on: "
                f"{', '.join(dependencies)})"
            )

        else:

            print(
                f"  {task['id']} → "
                f"{task['tool']} "
                f"(parallel-ready)"
            )

    # =================================================
    # RETURN STATE
    # =================================================

    print(
        "\n✅ SUPERVISOR FINISHED"
    )

    print(
        f"📋 Total executable tasks: "
        f"{len(valid_tasks)}"
    )

    print(
        "=============================================="
    )

    return {
        "execution_plan": valid_tasks,

        "routing_reason": reason,

        "next_agent": ",".join(
            task["tool"]
            for task in valid_tasks
        ),

        "active_tasks": [],

        "completed_tasks": [],

        "task_results": {},
    }