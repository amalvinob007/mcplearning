import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()


async def setup_turf_agent():
    """Setup the turf booking agent with MCP tools"""
    
    # Check for API keys - prioritize Groq
    if not os.getenv("GROQ_API_KEY") :
        raise ValueError(
            "Please set one of these API keys in your .env file:\n"
            "GROQ_API_KEY (recommended - fast and free)\n"
            "Get Groq API key from: https://console.groq.com/keys\n"
        )
    
    # Initialize the model - try Groq first, then others
    if os.getenv("GOOGLE_API_KEY"):
        # model = init_chat_model("groq:llama-3.3-70b-versatile")
        # model = init_chat_model("groq:llama-3.1-8b-instant")
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",   # or "gemini-1.5-pro"
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        # print("🤖 Using Groq Llama 3.3 70B model")
    
    # Set up MCP client for turf booking system
    client = MultiServerMCPClient(
        {
            "turf": {
                "command": "python",
                "args": ["turf_server.py"],  
                "transport": "stdio",
            }
        }
    )
    
    # Get tools from MCP server
    tools = await client.get_tools()
    print(f"🛠️ Available Tools: {[tool.name for tool in tools]}")
    
    # Bind tools to model
    model_with_tools = model.bind_tools(tools)
    
    # Create ToolNode
    tool_node = ToolNode(tools)
    
    def should_continue(state: MessagesState):
        """Determine whether to continue to tools or end"""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    
    # Define call_model function
    async def call_model(state: MessagesState):
        """Call the model with tools"""
        system_message = {
            "role": "system",
            "content": """You are a helpful turf booking assistant. You have access to these tools:

1. get_all_turfs() - Get all available turfs with details
2. get_all_bookings() - Get all current bookings  
3. check_turf_availability(turf_id, date) - Check availability for specific turf and date
4. make_booking(turf_id, customer_name, customer_phone, booking_date, start_time, end_time) - Make a booking

IMPORTANT INSTRUCTIONS:
- When users ask about turfs, bookings, availability, or want to make bookings, use the appropriate tool
- Always use the EXACT tool names: get_all_turfs, get_all_bookings, check_turf_availability, make_booking
- Display the complete output from tools - don't summarize
- For "show turfs", "list turfs", "what turfs" queries, use get_all_turfs()
- For "show bookings", "current bookings" queries, use get_all_bookings()
- For availability checks, use check_turf_availability(turf_id, date)
- For making bookings, use make_booking() with all required parameters

Examples:
- User: "Show me all turfs" → Call get_all_turfs()
- User: "Check availability for turf 1 on 2025-08-22" → Call check_turf_availability(1, "2025-08-22")
- User: "What are the current bookings?" → Call get_all_bookings()"""
        }
        
        messages = [system_message] + state["messages"]
        response = await model_with_tools.ainvoke(messages)
        
        # Debug information
        print(f"🔍 Model response type: {type(response)}")
        print(f"📜 Model response content: {response.content}")
        # if hasattr(response, 'tool_calls') and response.tool_calls:
        #     print(f"🔧 Tool calls: {[tc.get('name') for tc in response.tool_calls]}")
        # else:
        #     print("⚠️ No tool calls in response")
            
        return {"messages": [response]}

    
    # Build the graph
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        should_continue,
    )
    builder.add_edge("tools", "call_model")
    
    # Compile the graph
    graph = builder.compile()
    
    return graph, client

async def test_agent():
    """Test the turf booking agent"""
    print("🏟️ Setting up Turf Booking Agent...")
    print("=" * 60)
    
    try:
        graph, client = await setup_turf_agent()
        
        # # Test cases with more future dates
        # from datetime import datetime, timedelta
        # tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        # day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        # test_queries = [
        #     "Show me all available turfs",
        #     "What are all the current bookings?",
        #     f"Check availability for turf 1 on {tomorrow}",
        #     f"Book turf 2 for John Doe (phone: 9999888877) on {day_after} from 14:00 to 16:00"
        # ]
        
        # print("\n🧪 Testing Agent with Various Queries:")
        # print("=" * 60)
        
        # for i, query in enumerate(test_queries, 1):
        #     print(f"\n{i}. Query: {query}")
        #     print("-" * 50)
            
        #     try:
        #         response = await graph.ainvoke(
        #             {"messages": [{"role": "user", "content": query}]}
        #         )
                
        #         # Get the last assistant message
        #         last_message = response["messages"][-1]
        #         print(f"Response: {last_message.content}")
                
        #     except Exception as e:
        #         print(f"❌ Error: {e}")
        
        # Interactive mode
        print("\n" + "=" * 60)
        print("🎯 INTERACTIVE MODE")
        print("=" * 60)
        print("\nAvailable operations:")
        print("• Ask about turfs: 'Show me all turfs' or 'What turfs are available?'")
        print("• Check bookings: 'Show all bookings' or 'What are the current bookings?'")
        print("• Check availability: 'Check availability for turf X on YYYY-MM-DD'")
        print("• Make booking: 'Book turf X for [name] on [date] from [start] to [end]'")
        print("• Type 'quit' to exit")
        
        while True:
            try:
                user_input = input("\n🎮 Your query: ").strip()
                
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 Processing...")
                response = await graph.ainvoke(
                    {"messages": [{"role": "user", "content": user_input}]}
                )
                
                # Get the last assistant message
                last_message = response["messages"][-1]
                print(f"\n📝 Response:\n{last_message}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Setup Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure you have a .env file with ANTHROPIC_API_KEY or OPENAI_API_KEY")
        print("2. Install required packages: pip install python-dotenv")
        print("3. Make sure turf_server.py is in the same directory")
        print("4. Check if the database.py file is properly set up")
        
    finally:
        # Close the client properly
        if 'client' in locals():
            await client.aclose()

async def main():
    """Main function"""
    await test_agent()

if __name__ == "__main__":
    asyncio.run(main())
    