# MCP Turf Booking V4 Final

This folder contains the final version of the MCP (Multi-Component Protocol) turf booking system, featuring a full backend, prompt server, agent, and a Streamlit UI.

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

- **prompt_server.py**  
  MCP server exposing prompt templates for common turf booking actions (check availability, list turfs, make booking, view bookings, booking summary).

- **turf_agent.py**  
  Agent code using LangChain MCP adapters to connect to the MCP server, bind tools to a language model, and interact with users.

- **sync_agent.py**  
  Synchronous wrapper for the agent, allowing integration with Streamlit UI.

- **simple_app.py**  
  Streamlit UI for interacting with the turf booking agent.  
  Supports both chat mode and smart prompt forms for booking, checking availability, viewing bookings, and summaries.

## How to Run

1. **Initialize the database**  
   (Optional: The database is auto-initialized when running the server or database.py)
   ```bash
   python database.py
   ```

2. **Start the Streamlit UI**  
   ```bash
   streamlit run simple_app.py
   ```

   - The UI will launch in your browser.
   - You can chat with the agent or use smart prompt forms for quick actions.

3. **(Optional) Run backend servers directly**  
   - Start the turf server:
     ```bash
     python turf_server.py
     ```
   - Start the prompt server:
     ```bash
     python prompt_server.py
     ```

4. **(Optional) Run the agent for CLI testing**  
   ```bash
   python turf_agent.py
   ```

## Notes

- All data is stored in a local SQLite database (`turf_booking.db`).
- You need API keys for LLM integration (set in your `.env` file).
- The UI supports both chat and form-based interactions.
- You can extend the tools and prompts by editing `resources/server_all.py` and `prompt_server.py`.

## Frontend UI Screenshots

Below are screenshots of the Streamlit UI:

### Home Page

![Home Page](MCP_LEARNING/4_Use_Case/Turf_booking_V4_Final/Output_img/Front_page.png)

### Chat_interface

![Chat](MCP_LEARNING/4_Use_Case/Turf_booking_V3_Final/Output_img/chat_interface.png)

### Prompt interface

![Chat Interface](MCP_LEARNING/4_Use_Case/Turf_booking_V3_Final/Output_img/Prompt_input.png)





