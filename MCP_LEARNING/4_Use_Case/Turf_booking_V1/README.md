# MCP Turf Booking V1

This folder contains a simple MCP (Multi-Component Protocol) implementation for a turf booking system.  
It demonstrates how to expose resources and tools for turf management using MCP, with a SQLite backend.

## Files Overview

- **database.py**  
  Initializes the SQLite database with sample turfs and bookings.

- **resources/server_all.py**  
  Contains backend functions for listing turfs, bookings, checking availability, and booking a turf.

- **resources/client_all.py**  
  Provides client-side helper functions to test resources and tools, and an interactive mode.

- **turf_server.py**  
  MCP server exposing resources and tools for turf booking.  
  Resources:  
    - `turf://all` (all turfs)  
    - `turf://bookings/all` (all bookings)  
    - `turf://availability/{turf_id}/{date}` (availability for a turf on a date)  
  Tool:  
    - `make_booking` (create a new booking)

- **client.py**  
  MCP client that connects to the server, lists resources/tools, tests them, and provides an interactive CLI.

## How to Run

1. **Initialize the database**  
   (Optional: The database is auto-initialized when running the server or database.py)
   ```bash
   python database.py
   ```

2. **Start the MCP client**  
   (This will automatically start the server as a subprocess)
   ```bash
   python client.py
   ```

   - The client will:
     - List available resources and tools
     - Test reading resources (turfs, bookings, availability)
     - Test booking creation and error cases
     - Provide an interactive mode for manual testing

3. **(Optional) Run the server directly**  
   ```bash
   python turf_server.py
   ```
   - You will need a compatible MCP client to interact with the server.

## Notes

- All data is stored in a local SQLite database (`turf_booking.db`).
- You can extend the resources and tools by editing `resources/server_all.py`.
- The interactive mode in `client.py` allows you to manually test booking and resource queries.

