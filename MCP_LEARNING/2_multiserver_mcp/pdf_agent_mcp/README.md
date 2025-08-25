# Multi-Server MCP Agents: Math, Weather, Calculator

This folder demonstrates how to use MCP (Multi-Component Protocol) with multiple servers to build a modular assistant that can handle math calculations, weather queries, and general calculator operations.

## Structure

- **Math Agent**  
  Exposes `add` and `multiply` tools for math operations.

- **Weather Agent** (`pdf_agent_mcp/weather_agent.py`):  
  Exposes a `get_weather` tool using WeatherAPI to provide current weather information for any location.

- **Calculator Agent**   
  Exposes `add` and `multiply` tools for basic calculator functionality.

- **PDF Agent** (`pdf_agent.py`):  
  Exposes tools for loading, querying, and summarizing PDF documents.

- **MultiServer Client/Agent** (`pdf_agent_mcp/stdio_server.py`)  
  Uses `MultiServerMCPClient` to connect to multiple MCP servers, aggregate their tools, and interact with them via a language model agent (e.g., Groq LLM).

## How It Works

- Each agent runs as a separate MCP server, exposing its own set of tools.
- The main agent script (`stdio_server.py`) launches all servers, collects their tools, and binds them to a language model.
- The agent can answer questions by invoking the appropriate tool from the relevant server (math, weather, calculator, or PDF).

## Running the Example

1. **Start the main agent** (which launches all MCP servers automatically):

   ```bash
   python pdf_agent_mcp/stdio_server.py
   ```

   or

   ```bash
   python stdio_server.py
   ```

2. **Interact with the agent**  
   - Ask math questions: `What's (3 + 5) x 12?`
   - Ask for weather: `What's the weather in Chennai?`
   - Use calculator: `Add 7 and 8`
   - Work with PDFs: `Load the PDF at /path/to/file.pdf` then `What is the summary of the PDF?`

## Requirements

- Python 3.8+
- MCP Python package (`mcp`)
- LangChain, LangGraph, LangChain Groq (for LLM integration)
- WeatherAPI key (set as `WEATHER_API_KEY` in your environment)
- Groq API key (set as `GROQ_API_KEY` in your environment)
- pdfplumber (for PDF agent)

## Notes

- The multi-server architecture allows you to add or remove agents easily.
- Each agent is responsible for a specific domain (math, weather, calculator, PDF).
- The main agent aggregates all tools and routes user queries to the correct agent/tool.
- You can extend this setup by adding more agents for other domains.

