# Multi-Server MCP Math Calculator

This example demonstrates how to use MCP (Multi-Component Protocol) with multiple servers to build a math calculator agent. The agent can perform addition and multiplication by calling tools exposed by an MCP server.

## Structure

- `agent_tool.py`: MCP server exposing `add` and `multiply` tools.
- `stdio_server.py`: Python script that launches the MCP server, connects using `MultiServerMCPClient`, and interacts with the tools via a language model agent.

## How It Works

1. **MCP Server (`agent_tool.py`)**  
   - Implements two tools: `add(a, b)` and `multiply(a, b)`.
   - Runs with stdio transport for easy integration.

2. **Agent (`stdio_server.py`)**  
   - Uses `MultiServerMCPClient` to connect to the MCP server.
   - Loads available tools and binds them to a language model (Groq LLM in this example).
   - Uses the ReAct agent pattern to answer math questions by invoking the appropriate tools.

## Running the Example

1. **Start the agent** (which will launch the MCP server automatically):

   ```bash
   python stdio_server.py
   ```

   The agent will connect to the MCP server, load the tools, and process a sample math question.

2. **Expected Output**  
   You should see debug output for tool calls and the agent's response to the math question.

## Requirements

- Python 3.8+
- MCP Python package (`mcp`)
- LangChain and LangGraph packages
- Groq API key (for LLM, or replace with your preferred LLM)

## Notes

- The agent can be extended to support more math operations by adding tools to `agent_tool.py`.
- The multi-server setup allows for modular and scalable tool integration.
- The example uses stdio transport for simplicity, but other transports are supported by MCP.

