from fastmcp import FastMCP
from core.auth import MyTokenVerifier

from tools.database_tools import (
    initialize_database,
    add_employee,
    get_all_employees,
    find_employee_by_id,
    update_employee_salary,
    delete_employee,
    find_employee_by_department,
    find_employee_by_min_salary,
    find_employee_by_salary_range,
    get_highest_paid_employee,
    get_average_salary,
    get_employee_count_by_department,
    get_average_salary_by_department,
    get_departments_with_more_than,
)

auth = MyTokenVerifier()

mcp = FastMCP(
    "Database Server",
    auth=auth
)

@mcp.tool()
def initialize_db():
    """Initialize the database"""
    return initialize_database()

@mcp.tool()
def add_new_employee(name: str, department: str, salary: float):
    """Add a new employee to the database"""
    return add_employee(name, department, salary)

@mcp.tool()
def get_all_employees_from_db():
    """Get all employees from the database"""
    return get_all_employees()

@mcp.tool()
def find_employee_id(employee_id: int):
    """Find an employee by their id"""
    return find_employee_by_id(employee_id)

@mcp.tool()
def update_salary_by_id(employee_id: int, salary: float):
    """Update an employees salary by their id"""
    return update_employee_salary(employee_id, salary)

@mcp.tool()
def delete_employee_by_id(employee_id: int):
    """Delete an employee by their id"""
    return delete_employee(employee_id)

@mcp.tool()
def find_employee_by_department_name(department: str):
    """Find employees by their department"""
    return find_employee_by_department(department)

@mcp.tool()
def find_employee_with_min_salary(min_salary: float):
    """Find the employee with the min_salary"""
    return find_employee_by_min_salary(min_salary)

@mcp.tool()
def find_employee_with_salary_range_tool(min_salary: float, max_salary: float):
    """Find employees with salary between the given min and max."""
    return find_employee_by_salary_range(min_salary, max_salary)

@mcp.tool()
def find_highest_paid_employee():
    """Highest paid employee"""
    return get_highest_paid_employee()

@mcp.tool()
def find_avg_salary_tool():
    """Average salary for the employee"""
    return get_average_salary()

@mcp.tool()
def find_employee_count_by_department():
    """Count of employee by department"""
    return get_employee_count_by_department()

@mcp.tool()
def find_avg_salary_by_department():
    """Average salary for each department"""
    return get_average_salary_by_department()

@mcp.tool()
def find_department_with_more(employee_count: int):
    """Find departments with more than the given employee count."""
    return get_departments_with_more_than(employee_count)

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001
    )