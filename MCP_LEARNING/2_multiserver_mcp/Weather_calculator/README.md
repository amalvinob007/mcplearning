# Multi-Server MCP: Weather & Math Calculator

This folder demonstrates how to use MCP (Multi-Component Protocol) with multiple servers to build an assistant that can answer both math and weather queries.

## Structure

- `math_agent.py`: MCP server exposing `add` and `multiply` tools for math operations.
- `weather_agent.py`: MCP server exposing `get_weather` tool using WeatherAPI for current weather information.
- `stdio_server.py`: Python script that launches both MCP servers, aggregates their tools, and interacts with them via a language model agent.

## How It Works

- Each agent runs as a separate MCP server, exposing its own set of tools.
- The main script (`stdio_server.py`) launches both servers, collects their tools, and binds them to a language model (Groq LLM).
- The agent can answer math questions (using `add` and `multiply`) and weather queries (using `get_weather`).

## Running the Example

1. **Set your API keys**  
   - Set `WEATHER_API_KEY` in your environment for WeatherAPI.
   - Set `GROQ_API_KEY` for Groq LLM.

2. **Start the main agent** (which launches both MCP servers automatically):

   ```bash
   python stdio_server.py
   ```

3. **Example Queries**
   - Math: `What's (3 * 5) + 7?`
   - Weather: `What's the weather in Chennai?`

## Requirements

- Python 3.8+
- MCP Python package (`mcp`)
- LangChain, LangGraph, LangChain Groq (for LLM integration)
- WeatherAPI key
- Groq API key

## Notes

- The multi-server architecture allows you to add more agents easily.
- Each agent is responsible for a specific domain (math or weather).
- The main agent aggregates all tools and routes user queries to the correct agent/tool.

