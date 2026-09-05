# from langchain_core.messages import (
#     HumanMessage,
#     SystemMessage,
# )


# EMPLOYEE_TOOL_NAMES = {
#     "initialize_db",
#     "add_new_employee",
#     "get_all_employees_from_db",
#     "find_employee_id",
#     "update_salary_by_id",
#     "delete_employee_by_id",
#     "find_employee_by_department_name",
#     "find_employee_with_min_salary",
#     "find_employee_with_salary_range_tool",
#     "find_highest_paid_employee",
#     "find_avg_salary_tool",
#     "find_employee_count_by_department",
#     "find_avg_salary_by_department",
#     "find_department_with_more",
# }


# async def employee_agent(state, config):

#     llm = config["configurable"]["llm"]

#     messages = state["messages"]

#     # =============================================
#     # GET USER REQUEST
#     # =============================================

#     user_request = ""

#     for message in reversed(messages):

#         if isinstance(message, HumanMessage):

#             user_request = message.content

#             break

#     # =============================================
#     # GET ALL MCP TOOLS
#     # =============================================

#     all_tools = config["configurable"]["tools"]

#     # =============================================
#     # FILTER EMPLOYEE TOOLS
#     # =============================================

#     employee_tools = [
#         tool
#         for tool in all_tools
#         if tool.name in EMPLOYEE_TOOL_NAMES
#     ]

#     # =============================================
#     # BIND ONLY EMPLOYEE TOOLS
#     # =============================================

#     employee_llm = llm.bind_tools(
#         employee_tools
#     )

#     # =============================================
#     # SYSTEM PROMPT
#     # =============================================

#     system_prompt = """
# You are the Employee Agent.

# Your responsibility is ONLY employee and
# employee-database related operations.

# You have access to employee MCP tools.

# Use the appropriate MCP tool when the user
# requests employee information or an employee
# database operation.

# Examples:

# Find employee 1
# → find_employee_id

# List all employees
# → get_all_employees_from_db

# Update employee 1 salary
# → update_salary_by_id

# Delete employee 1
# → delete_employee_by_id

# Find employees in IT
# → find_employee_by_department_name

# Find highest paid employee
# → find_highest_paid_employee

# Important:

# - Do not invent employee information.
# - Do not perform file operations.
# - Do not perform weather operations.
# - Do not send emails directly.
# - Risk analysis and human approval are handled
#   by the application.
# - If a tool is required, call the tool directly.
# """

#     # =============================================
#     # CALL EMPLOYEE LLM
#     # =============================================

#     response = await employee_llm.ainvoke(
#         [
#             SystemMessage(
#                 content=system_prompt
#             ),
#             *messages,
#         ]
#     )

#     print(
#         "\n👤 EMPLOYEE AGENT"
#     )

#     return {
#         "messages": [response]
#     }