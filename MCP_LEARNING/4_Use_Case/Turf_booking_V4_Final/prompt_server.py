from mcp.server import Server
import mcp.types as types
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Define available prompts for turf booking
PROMPTS = {
    "check-availability": types.Prompt(
        name="check-availability",
        description="Check turf availability for a specific date and turf",
        arguments=[
            types.PromptArgument(
                name="turf_id",
                description="ID of the turf to check",
                required=True
            ),
            types.PromptArgument(
                name="date",
                description="Date to check availability (YYYY-MM-DD format)",
                required=True
            ),
            types.PromptArgument(
                name="preferred_time",
                description="Preferred time slot (optional, e.g., '14:00-16:00')",
                required=False
            )
        ],
    ),
    "list-turfs": types.Prompt(
        name="list-turfs",
        description="Get information about all available turfs",
        arguments=[
            types.PromptArgument(
                name="filter_by",
                description="Optional filter (e.g., 'location', 'price_range')",
                required=False
            )
        ],
    ),
    "make-booking": types.Prompt(
        name="make-booking",
        description="Make a turf booking with customer details",
        arguments=[
            types.PromptArgument(
                name="turf_id",
                description="ID of the turf to book",
                required=True
            ),
            types.PromptArgument(
                name="customer_name",
                description="Customer's name",
                required=True
            ),
            types.PromptArgument(
                name="customer_phone",
                description="Customer's phone number",
                required=True
            ),
            types.PromptArgument(
                name="booking_date",
                description="Date for booking (YYYY-MM-DD)",
                required=True
            ),
            types.PromptArgument(
                name="start_time",
                description="Start time (HH:MM format)",
                required=True
            ),
            types.PromptArgument(
                name="end_time",
                description="End time (HH:MM format)",
                required=True
            )
        ],
    ),
    "view-bookings": types.Prompt(
        name="view-bookings",
        description="View current bookings",
        arguments=[
            types.PromptArgument(
                name="date_filter",
                description="Optional date to filter bookings (YYYY-MM-DD)",
                required=False
            ),
            types.PromptArgument(
                name="turf_filter",
                description="Optional turf ID to filter bookings",
                required=False
            )
        ],
    ),
    "booking-summary": types.Prompt(
        name="booking-summary",
        description="Generate a booking summary and recommendations",
        arguments=[
            types.PromptArgument(
                name="turf_id",
                description="Turf ID for the summary",
                required=True
            ),
            types.PromptArgument(
                name="date_range",
                description="Date range for summary (e.g., 'this_week', 'next_month')",
                required=False
            )
        ],
    )
}

# Initialize server
app = Server("turf-booking-prompts-server")

@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List all available prompts"""
    return list(PROMPTS.values())

@app.get_prompt()
async def get_prompt(
    name: str, arguments: dict[str, str] | None = None
) -> types.GetPromptResult:
    """Get a specific prompt with arguments"""
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")
    
    # Default arguments if none provided
    args = arguments or {}
    
    if name == "check-availability":
        turf_id = args.get("turf_id", "")
        date = args.get("date", "")
        preferred_time = args.get("preferred_time", "")
        
        time_context = f" for preferred time {preferred_time}" if preferred_time else ""
        
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Check the availability of turf {turf_id} on {date}{time_context}. "
                        f"Please use the check_turf_availability tool and show me all available time slots "
                        f"along with any existing bookings. Also provide the turf details like location and rates."
                    )
                )
            ]
        )
    
    elif name == "list-turfs":
        filter_by = args.get("filter_by", "")
        filter_context = f" filtered by {filter_by}" if filter_by else ""
        
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Show me all available turfs{filter_context}. "
                        f"Please use the get_all_turfs tool and display the complete information including "
                        f"IDs, names, locations, rates per hour, capacity, and facilities for each turf."
                    )
                )
            ]
        )
    
    elif name == "make-booking":
        turf_id = args.get("turf_id", "")
        customer_name = args.get("customer_name", "")
        customer_phone = args.get("customer_phone", "")
        booking_date = args.get("booking_date", "")
        start_time = args.get("start_time", "")
        end_time = args.get("end_time", "")
        
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please make a booking for turf {turf_id} with the following details:\n"
                        f"Customer Name: {customer_name}\n"
                        f"Phone: {customer_phone}\n"
                        f"Date: {booking_date}\n"
                        f"Time: {start_time} to {end_time}\n\n"
                        f"Use the make_booking tool to process this booking. First check if the slot is available, "
                        f"then proceed with the booking and provide confirmation details including total cost."
                    )
                )
            ]
        )
    
    elif name == "view-bookings":
        date_filter = args.get("date_filter", "")
        turf_filter = args.get("turf_filter", "")
        
        filter_text = ""
        if date_filter and turf_filter:
            filter_text = f" for turf {turf_filter} on {date_filter}"
        elif date_filter:
            filter_text = f" for {date_filter}"
        elif turf_filter:
            filter_text = f" for turf {turf_filter}"
        
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Show me all current bookings{filter_text}. "
                        f"Please use the get_all_bookings tool and display the booking information "
                        f"in a clear, organized format including booking IDs, turf names, dates, times, "
                        f"costs, and status."
                    )
                )
            ]
        )
    
    elif name == "booking-summary":
        turf_id = args.get("turf_id", "")
        date_range = args.get("date_range", "current")
        
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Generate a comprehensive summary for turf {turf_id} ({date_range}). "
                        f"Please:\n"
                        f"1. Use get_all_turfs to get turf details\n"
                        f"2. Use get_all_bookings to get booking information\n"
                        f"3. Use check_turf_availability to check upcoming availability\n\n"
                        f"Provide insights on booking patterns, popular time slots, revenue information, "
                        f"and recommendations for optimal booking times."
                    )
                )
            ]
        )
    
    raise ValueError("Prompt implementation not found")

# Standalone LLM processor for prompts
class PromptLLMProcessor:
    def __init__(self):
        """Initialize the LLM for processing prompts"""
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    async def process_prompt(self, prompt_name: str, arguments: dict = None) -> str:
        """Process a prompt and return LLM response"""
        try:
            # Get the prompt
            prompt_result = await get_prompt(prompt_name, arguments)
            
            # Extract the prompt text
            message = prompt_result.messages[0]
            prompt_text = message.content.text
            
            # Process with LLM
            response = await self.model.ainvoke(prompt_text)
            
            return response.content
            
        except Exception as e:
            return f"Error processing prompt: {str(e)}"

# Global processor instance
prompt_processor = None

async def initialize_processor():
    """Initialize the prompt processor"""
    global prompt_processor
    try:
        prompt_processor = PromptLLMProcessor()
        print("✅ Prompt LLM Processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")

async def process_prompt_request(prompt_name: str, arguments: dict = None) -> str:
    """Public function to process prompt requests"""
    global prompt_processor
    if not prompt_processor:
        await initialize_processor()
    
    if not prompt_processor:
        return "❌ Prompt processor not available"
    
    return await prompt_processor.process_prompt(prompt_name, arguments)

if __name__ == "__main__":
    # Run the MCP server
    import mcp.server.stdio
    async def main():
        await initialize_processor()
        await mcp.server.stdio.run_server(app)
    
    asyncio.run(main())