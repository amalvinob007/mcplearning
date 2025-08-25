# MCP Resource & Prompt Example

This folder demonstrates how to use MCP (Multi-Component Protocol) to expose resources and prompt templates via a Python server. The example includes a simple greeting resource and a code review prompt.

## Structure

- `server.py`: MCP server exposing a greeting resource and a code review prompt.
- `client.py`: MCP client that connects to the server, lists resources and prompts, and demonstrates fetching and rendering them.

## Features

- **Resource**:
  - `greeting://{name}`: Returns a personalized greeting for the given name.

- **Prompt**:
  - `code_review(language, code)`: Renders a prompt for code review in the specified language.

## How It Works

- The server exposes resources using MCP's `@resource` decorator and prompts using `@prompt`.
- The client connects to the server, lists available resources and prompts, and demonstrates fetching and rendering them.

## Running the Example

1. **Start the client** (which will launch the server automatically):

   ```bash
   python client.py
   ```

   You will see output showing available prompts, resources, and sample data fetched from the server.

2. **(Optional) Run the server directly**:

   ```bash
   python server.py
   ```

   The server will start and wait for MCP client connections.

## Requirements

- Python 3.8+
- MCP Python package (`mcp`)

## Notes

- You can extend the server to expose more resources or prompts as needed.
- The resource URIs are flexible and can be used for other types of data or services.
- This example is intended for learning and demonstration purposes.

