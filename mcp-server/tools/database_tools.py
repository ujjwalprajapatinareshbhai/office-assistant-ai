import sqlite3
from pathlib import Path

DB_PATH = Path("database")/"office.db"

def initialize_database():
    """Initializes the SQLITE database by creating the necessary tables if they do not exist."""
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        salary REAL NOT NULL)
        """)

    conn.commit()

    conn.close()

    return "Database initialized successfully."


def add_employee(name:str,department:str,salary:float):
    """Adds a new employee to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO employees(name, department, salary) VALUES (?, ?, ?)""",
        (name, department, salary)
    )
    conn.commit()
    conn.close()
    return "Employee added successfully."

def get_all_employees():
    """Retrieves all employees from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""Select * from employees""")
    employees = cursor.fetchall()
    conn.close()
    return employees

def find_employee_by_id(employee_id:int):
    """Finds an employee by their id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("Select * FROM employees where id = ?", (employee_id,))
    employee = cursor.fetchone()
    conn.close()
    return employee

def update_employee_salary(employee_id:int,salary:float):
    """Update an employee's salary in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE employees SET salary = ? WHERE id = ?""",
        (salary,employee_id)
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return f"No employee found with id {employee_id}."
    conn.close()
    return "Employee Salary updated successfully."

def delete_employee(employee_id: int):
    """Delete an employee from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM employees WHERE id = ?",(employee_id,)
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return f"No employee found with this id {employee_id}"
    conn.close()
    return f"Employee with id {employee_id} deleted successfully"

def find_employee_by_department(department:str):
    """Finds employees by their department"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE LOWER(department) = LOWER(?)",(department,))
        employees = cursor.fetchall()
        return employees
    finally:
        conn.close()

def find_employee_by_min_salary(min_salary:float):
    """Find employees earning at least the min_salary"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees where salary >= ?",(min_salary,))
        employees = cursor.fetchall()
        return employees
    finally:
        conn.close()

def find_employee_by_salary_range(min_salary:float,max_salary:float):
    """Find the employees whose salary is between min_salary and max_salary"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees where salary between ? and ?",(min_salary,max_salary))
        employee = cursor.fetchall()
        return employee
    finally:
        conn.close()

def get_highest_paid_employee():
    """Return the employee with the highest salary"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY salary DESC LIMIT 1")
        employee = cursor.fetchone()
        return employee 
    finally:
        conn.close()

def get_average_salary():
    """Return the average salary of all employees."""
    conn= sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(salary) FROM employees")
        employee = cursor.fetchone()[0]
        return employee
    finally:
        conn.close()

def get_employee_count_by_department():
    """Return the number of employees in each department."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT department, COUNT(*) FROM employees GROUP BY department")
        employee = cursor.fetchall()
        return employee
    finally:
        conn.close()

def get_average_salary_by_department():
    """Return the average salary for each department."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT department, avg(salary) FROM employees GROUP BY department")
        employee =cursor.fetchall()
        return employee
    finally:
        conn.close()

def get_departments_with_more_than(employee_count: int):
    """Return departments having more than the given number of employees."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT department, COUNT(*) FROM employees GROUP BY department HAVING COUNT(*) > ?", (employee_count,))
        employee = cursor.fetchall()
        return employee
    finally:
        conn.close()

    
