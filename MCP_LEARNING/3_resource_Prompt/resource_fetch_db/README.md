# MCP Resource & Prompt Example: Employee Database

This folder demonstrates how to use MCP (Multi-Component Protocol) to expose database resources and prompt templates via a Python server. The example uses a simple SQLite database of employees and provides both static and dynamic resource endpoints, as well as a code review prompt.

## Structure

- `server.py`: MCP server exposing database resources and a prompt template.
- `client.py`: MCP client that connects to the server, lists resources/prompts, and fetches data.

## Features

- **Resources**:
  - `greeting://{name}`: Returns a personalized greeting.
  - `db://employees/all`: Lists all employees.
  - `db://employees/department/{dept}`: Lists employees by department.
  - `db://employees/id/{emp_id}`: Gets details for a specific employee by ID.

- **Prompt**:
  - `code_review(language, code)`: Renders a prompt for code review in the specified language.

## How It Works

- The server initializes a SQLite database with sample employee data.
- Resources are exposed using MCP's `@resource` decorator, allowing clients to fetch data using URI-like endpoints.
- The prompt template is exposed using MCP's `@prompt` decorator.
- The client connects to the server, lists available resources and prompts, and demonstrates fetching data and rendering prompts.

## Running the Example

1. **Start the client** (which will launch the server automatically):

   ```bash
   python client.py
   ```

   You will see output showing available prompts, resources, and sample data fetched from the database.

2. **(Optional) Run the server directly**:

   ```bash
   python server.py
   ```

   The server will start and wait for MCP client connections.

## Requirements

- Python 3.8+
- MCP Python package (`mcp`)
- SQLite (built-in with Python)

## Notes

- You can extend the server to expose more resources or prompts as needed.
- The resource URIs are flexible and can be used for other types of data or services.
- This example is intended for learning and demonstration purposes.

