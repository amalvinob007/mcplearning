# MCP Turf Booking V2 Tools

This folder contains an improved MCP (Multi-Component Protocol) implementation for a turf booking system, using only tools (no resources).  
It demonstrates how to expose turf management operations as MCP tools, with a SQLite backend and agent integration.

## Files Overview

- **database.py**  
  Initializes the SQLite database with sample turfs and bookings.

- **resources/server_all.py**  
  Contains backend functions for listing turfs, bookings, checking availability, and booking a turf.

- **turf_server.py**  
  MCP server exposing all turf operations as tools:
    - `get_all_turfs`: List all turfs
    - `get_all_bookings`: List all bookings
    - `check_turf_availability`: Check availability for a turf on a date
    - `make_booking`: Create a new booking

- **turf_agent.py**  
  Example agent code using LangChain MCP adapters to connect to the MCP server, bind tools to a language model, and interact with users (includes interactive mode).

- **sample_test.py**  
  Simple script to test MCP tools by calling them and printing results.

## How to Run

1. **Initialize the database**  
   (Optional: The database is auto-initialized when running the server or database.py)
   ```bash
   python database.py
   ```

2. **Start the MCP server**  
   ```bash
   python turf_server.py
   ```

   - The server will expose all turf operations as MCP tools.

3. **Test the tools**  
   ```bash
   python sample_test.py
   ```

   - This will connect to the server, list available tools, and test each tool.

4. **Run the agent (optional, for advanced usage)**  
   ```bash
   python turf_agent.py
   ```

   - The agent will connect to the MCP server, bind tools to a language model, and allow interactive queries (requires API keys for LLM).

## Notes

- All data is stored in a local SQLite database (`turf_booking.db`).
- You can extend the tools by editing `resources/server_all.py` and `turf_server.py`.
- The agent integration demonstrates how to use MCP tools with LangChain and LLMs.

