# server.py
import sqlite3
import json
from fastmcp import FastMCP

mcp = FastMCP("demo-python")

# Initialize SQLite database
def init_db():
    """Create a simple database with sample data"""
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL,
            hire_date TEXT
        )
    """)
    
    # Insert sample data (only if table is empty)
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            (1, "Alice Johnson", "Engineering", 75000, "2022-01-15"),
            (2, "Bob Smith", "Marketing", 62000, "2021-06-20"),
            (3, "Carol Davis", "Engineering", 80000, "2020-03-10"),
            (4, "David Wilson", "HR", 58000, "2023-02-01"),
            (5, "Eva Brown", "Engineering", 85000, "2019-09-12")
        ]
        
        cursor.executemany(
            "INSERT INTO employees (id, name, department, salary, hire_date) VALUES (?, ?, ?, ?, ?)",
            sample_data
        )
        conn.commit()
        print("Database initialized with sample data")
    
    conn.close()

# Initialize database on server start
init_db()

# EXISTING: Dynamic greeting resource
@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Personalized greeting resource"""
    return f"Hello, {name}!"

# NEW: Static resource - all employees
@mcp.resource("db://employees/all")
def get_all_employees() -> str:
    """Get all employees from database"""
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM employees ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No employees found"
    
    result = "All Employees:\n\n"
    for row in rows:
        result += f"ID: {row[0]}, Name: {row[1]}, Dept: {row[2]}, Salary: ${row[3]:,.2f}, Hired: {row[4]}\n"
    
    return result

# NEW: Dynamic resource - employee by department
@mcp.resource("db://employees/department/{dept}")
def get_employees_by_department(dept: str) -> str:
    """Get employees by department"""
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM employees WHERE LOWER(department) = LOWER(?) ORDER BY name", (dept,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return f"No employees found in {dept} department"
    
    result = f"Employees in {dept} Department:\n\n"
    for row in rows:
        result += f"ID: {row[0]}, Name: {row[1]}, Salary: ${row[3]:,.2f}, Hired: {row[4]}\n"
    
    return result

# NEW: Dynamic resource - employee by ID
@mcp.resource("db://employees/id/{emp_id}")
def get_employee_by_id(emp_id: str) -> str:
    """Get specific employee by ID"""
    try:
        emp_id_int = int(emp_id)
    except ValueError:
        return f"Invalid employee ID: {emp_id}"
    
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id_int,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return f"Employee with ID {emp_id} not found"
    
    return f"Employee Details:\nID: {row[0]}\nName: {row[1]}\nDepartment: {row[2]}\nSalary: ${row[3]:,.2f}\nHire Date: {row[4]}"

# EXISTING: Prompt template
@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Ask the model to review code"""
    return f"Please review this {language} code:\n\n```{language}\n{code}\n```"

if __name__ == "__main__":
    mcp.run()  # stdio by default