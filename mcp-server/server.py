# import os
# from dotenv import load_dotenv
# from fastmcp import FastMCP,Context
# from fastmcp.server.auth import TokenVerifier, AccessToken

# load_dotenv()

# API_KEY = os.getenv("MCP_API_KEY")


# class MyTokenVerifier(TokenVerifier):

#     async def verify_token(self, token: str) -> AccessToken | None:

#         print("=" * 50)
#         print("verify_token() called")
#         print(f"Received token: {token}")
#         print(f"Expected token: {API_KEY}")

#         if token == API_KEY:
#             print("✅ Token is VALID")

#             return AccessToken(
#                 token=token,
#                 client_id="cursor",
#                 scopes=[]
#             )

#         print("❌ Token is INVALID")
#         return None
    
# from tools.calculator_tools import calculate
# from tools.database_tools import (
#     add_employee,
#     delete_employee,
#     find_employee_by_department,
#     find_employee_by_id,
#     find_employee_by_min_salary,
#     find_employee_by_salary_range,
#     get_average_salary,
#     get_average_salary_by_department,
#     get_departments_with_more_than,
#     get_employee_count_by_department,
#     get_highest_paid_employee,
#     get_all_employees,
#     initialize_database,
#     update_employee_salary,
# )
# from tools.email_tools import send_email
# from tools.excel_reader import read_excel
# from tools.file_tools import (
#     append_file,
#     delete_file,
#     list_files,
#     read_file,
#     rename_file,
#     search_files,
#     write_file,
# )
# from tools.folder_tools import create_folder, delete_folder, move_file
# from tools.notes_tools import append_note, read_notes
# from tools.pdf_reader import read_pdf
# from tools.prompt_tools import load_prompt
# from tools.report_tools import create_report
# from tools.resource_tools import read_resource_file
# from tools.search_tools import search,search_all_file
# from tools.system_tools import system_info
# from tools.weather_tools import get_weather, get_weather_forecast
# import time

# auth = MyTokenVerifier()
# mcp = FastMCP("Office Assistant",auth=auth)

# @mcp.tool()
# def hello():
#     """Test Mcp tool"""
#     return "Hello from FastMCP!"

# # FILES #

# @mcp.tool()
# def get_file(file_name:str):
#     """Read files from office folder"""
#     return read_file(file_name)

# @mcp.tool()
# def get_file_list():
#     """List files in office folder"""
#     return list_files()

# @mcp.tool()
# def create_file(file_name: str, content: str):
#     """Create a file in the office folder"""
#     return write_file(file_name, content)

# @mcp.tool()
# def append_to_file(file_name: str, content: str):
#     """Append content to a file in the office folder"""
#     return append_file(file_name, content)

# @mcp.tool()
# def rename_to_file(old_name: str, new_name: str):
#     """Rename a file in the office folder"""
#     return rename_file(old_name, new_name)

# @mcp.tool()
# def search_files_content(keyword: str) -> list[str]:
#     """Search for files containing a keyword."""
#     return search_files(keyword)

# @mcp.tool()
# def delete_a_file(file_name: str):
#     """Delete a file from the office folder."""
#     return delete_file(file_name)

# # DATABASE#

# @mcp.tool()
# def initialize_db():
#     """Initialize the database"""
#     return initialize_database()

# @mcp.tool()
# def add_new_employee(name: str, department: str, salary: float):
#     """Add a new employee to the database"""
#     return add_employee(name, department, salary)

# @mcp.tool()
# def get_all_employees_from_db():
#     """Get all employees from the database"""
#     return get_all_employees()

# @mcp.tool()
# def find_employee_id(employee_id: int):
#     """Find an employee by their id"""
#     return find_employee_by_id(employee_id)

# @mcp.tool()
# def update_salary_by_id(employee_id: int, salary: float):
#     """Update an employees salary by their id"""
#     return update_employee_salary(employee_id, salary)

# @mcp.tool()
# def delete_employee_by_id(employee_id: int):
#     """Delete an employee by their id"""
#     return delete_employee(employee_id)

# @mcp.tool()
# def find_employee_by_department_name(department: str):
#     """Find employees by their department"""
#     return find_employee_by_department(department)

# @mcp.tool()
# def find_employee_with_min_salary(min_salary: float):
#     """Find the employee with the min_salary"""
#     return find_employee_by_min_salary(min_salary)

# @mcp.tool()
# def find_employee_with_salary_range_tool(min_salary: float, max_salary: float):
#     """Find employees with salary between the given min and max."""
#     return find_employee_by_salary_range(min_salary, max_salary)

# @mcp.tool()
# def find_highest_paid_employee():
#     """Highest paid employee"""
#     return get_highest_paid_employee()

# @mcp.tool()
# def find_avg_salary_tool():
#     """Average salary for the employee"""
#     return get_average_salary()

# @mcp.tool()
# def find_employee_count_by_department():
#     """Count of employee by department"""
#     return get_employee_count_by_department()

# @mcp.tool()
# def find_avg_salary_by_department():
#     """Average salary for each department"""
#     return get_average_salary_by_department()

# @mcp.tool()
# def find_department_with_more(employee_count: int):
#     """Find departments with more than the given employee count."""
#     return get_departments_with_more_than(employee_count)

# # EMAIL#

# @mcp.tool()
# def send_a_email(to: str, subject: str, body: str):
#     """Send an email"""
#     return send_email(to, subject, body)

# # CALCULATE#

# @mcp.tool()
# def calculator(expression: str):
#     """Evaluate a mathematical expression"""
#     return calculate(expression)

# # WEATHER #

# @mcp.tool()
# def weather_update(city: str):
#     """Live Weather updated"""
#     return get_weather(city)

# @mcp.tool()
# def weather_forecast_update(city: str):
#     """Weather forecast for tomorrow"""
#     return get_weather_forecast(city, days=1)

# # PDF_READER #

# @mcp.tool()
# def get_pdf_reader(filename: str):
#     """Read the PDF file."""
#     return read_pdf(filename)

# # EXCEL_READER #

# @mcp.tool()
# def get_excel_reader(filename: str):
#     """Read the Excel file."""
#     return read_excel(filename)

# # FOLDER #

# @mcp.tool()
# def get_create_folder(folder_name: str):
#     """Create a new folder"""
#     return create_folder(folder_name)

# @mcp.tool()
# def delete_folder_tools(folder_name: str):
#     """Delete a folder."""
#     return delete_folder(folder_name)

# @mcp.tool()
# def move_file_tool(file_name: str, folder: str):
#     """Move a file from one folder to another."""
#     return move_file(file_name, folder)

# # NOTES #

# @mcp.tool()
# def append_note_tool(text: str):
#     """Add the new text into the existing file"""
#     return append_note(text)

# @mcp.tool()
# def read_note_tool():
#     """Read the text from the notes"""
#     return read_notes()

# # SEARCH_TOOL #

# @mcp.tool()
# def web_search(query: str):
#     """Search the web for the given query."""
#     return search(query)

# # SYSTEM_INFO #

# @mcp.tool()
# def get_system_info():
#     """Return system information."""
#     return system_info()

# # REPORT_TOOL #

# @mcp.tool()
# def generate_report_tool(
#     title: str, summary: str, details: str = "", sources: list[str] | None = None
# ):
#     """Generate a formatted report that can be displayed or emailed."""
#     return create_report(title, summary, details, sources)

# # RESOURCE #

# @mcp.resource("files://{filename}")
# def file_resource(filename: str):
#     """Read any file from the files directory."""
#     return read_resource_file(filename)

# # PROMPT_TOOL #

# @mcp.prompt
# def load_company_prompt(prompt_name: str):
#     """Load a prompt by name."""
#     return load_prompt(prompt_name)




# @mcp.tool()
# def stream_demo():
#     """Demonstrates streaming."""

#     yield "🚀 Starting..."

#     time.sleep(2)

#     yield "📂 Reading files..."

#     time.sleep(2)

#     yield "🌐 Searching..."

#     time.sleep(2)

#     yield "📝 Creating report..."

#     time.sleep(2)

#     yield "✅ Done!"


# @mcp.tool()
# def context_demo(name: str, ctx: Context):
#     """Simple context demo."""

#     ctx.info(f"context_demo called with name={name}")
    
#     return f"Hello {name}"

# @mcp.tool()
# async def search_from_all_files(keyword: str, ctx: Context):
#     """
#     Search all files for a keyword.
#     """
#     for message in search_all_file(keyword):

#         if message.message_type == "progress":
#             print(f"Progress: {message.current}/{message.total}")
#             await ctx.report_progress(
#                 progress=message.current,
#                 total=message.total,
#                 message = f"Searching {message.filename}"
#             )
#         elif message.message_type == "result":
#             return message.data
#         elif message.message_type == "error":
#             raise Exception (message.error)

# if __name__ == "__main__":
#     mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)