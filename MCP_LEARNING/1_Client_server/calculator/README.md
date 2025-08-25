# MCP Calculator Example

This folder demonstrates a simple client-server setup using the MCP (Multi-Component Protocol) framework for Python. The example implements a basic calculator service with two operations: addition and multiplication.

## Files

- `calculator_server.py`: MCP server exposing `add` and `multiply` tools.
- `calculator_client.py`: MCP client that connects to the server and calls the tools.

## How It Works

1. **Server**:  
   The server (`calculator_server.py`) defines two tools:
   - `add(a: int, b: int) -> int`: Returns the sum of two integers.
   - `multiply(a: int, b: int) -> int`: Returns the product of two integers.
   The server is started using MCP's FastMCP and listens for tool calls.

2. **Client**:  
   The client (`calculator_client.py`) launches the server as a subprocess, connects via stdio, and interacts with the server using MCP's client session. It lists available tools and demonstrates calling both `add` and `multiply`.

## Running the Example

1. **Start the client** (which will automatically start the server):

   ```bash
   python calculator_client.py
   ```

   You should see output showing the available tools and results of the operations.

2. **(Optional) Run the server directly**:

   ```bash
   python calculator_server.py
   ```

   This will start the server, but you need a compatible MCP client to interact with it.

## Requirements

- Python 3.8+
- MCP Python package (`mcp`)
- No external dependencies for the calculator logic

## Notes

- The client and server communicate using MCP's stdio transport.
- This example is intended for learning and demonstration purposes.

