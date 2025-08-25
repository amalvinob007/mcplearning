import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.callbacks import AsyncCallbackHandler
import os
from dotenv import load_dotenv
load_dotenv()
 
# API configuration

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
 
class ToolCallLogger(AsyncCallbackHandler):
    async def on_tool_start(self, serialized: dict, input: dict, **kwargs) -> None:
        print(f"🔧 Tool called: {serialized.get('name')} with input: {input}")
    async def on_tool_end(self, output, **kwargs) -> None:
        print(f"✅ Tool {kwargs.get('name')} output: {output}")
 
async def main():
    # Create MCP client with all agents
    client = MultiServerMCPClient(
        {
            "math agent": {
                "command": "python",
                "args": ["C:/Users/amal.vinob/Downloads/Amal/mcp/learning/mcp_agents/pdf_agent_mcp/math_agent.py"],
                "transport": "stdio",
            },
            "weather agent": {
                "command": "python",
                "args": ["C:/Users/amal.vinob/Downloads/Amal/mcp/learning/mcp_agents/pdf_agent_mcp/weather_agent.py"],
                "transport": "stdio",
            },
            "pdf agent": {
                "command": "python",
                "args": ["C:/Users/amal.vinob/Downloads/Amal/mcp/learning/mcp_agents/pdf_agent_mcp/pdf_agent.py"],
                "transport": "stdio",
            }
        }
    )
 
    # Get available tools from MCP servers
    tools = await client.get_tools()
    print(f"📋 Available tools: {[tool.name for tool in tools]}")
    
    # Enhanced system prompt to include PDF capabilities
    system_prompt = (
        "You are a versatile assistant capable of handling mathematical expressions, weather queries, and PDF document analysis. "
        "For mathematical expressions, break them down step-by-step, respecting operator precedence. "
        "Use the 'add' tool for addition and the 'multiply' tool for multiplication, ensuring all inputs are integers. "
        "For weather queries, use the 'get_weather' tool with the specified location. "
        "For PDF operations: First use 'load_pdf' to load a PDF file, then use 'ask_pdf_question' to answer questions about it. "
        "You can also use 'get_pdf_info' to get file information and 'list_loaded_pdfs' to see loaded files. "
        "If the query type is unclear, ask for clarification. Always provide clear, step-by-step reasoning."
    )
 
    # Groq LLM setup
    groq_llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile",
        # model= "llama-3.1-8b-instant",
    )
 
    # Create ReAct agent
    agent = create_react_agent(
        model=groq_llm,
        tools=tools,
    )
 
    print("/n" + "="*60)
    print("🧮 Testing Math Agent")
    print("="*60)
    
    # Test math calculation
    math_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "What's (3 * 5) + 7?"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}
    )
    print("🧮 Math Response:", math_response['messages'][-1].content)
 
    print("/n" + "="*60)
    print("🌤️ Testing Weather Agent")
    print("="*60)
    
    # Test weather query
    weather_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "What's the weather in Chennai?"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}
    )
    print("🌤️ Weather Response:", weather_response['messages'][-1].content)

    print("/n" + "="*60)
    print("📄 Testing PDF Agent")
    print("="*60)
    
    # Test PDF operations
    # First, let's check what PDF tools are available
    pdf_list_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "List any currently loaded PDF files"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}
    )
    print("📚 PDF List Response:", pdf_list_response['messages'][-1].content)
    
    
    
    pdf_load_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Load the PDF file at C:/Users/amal.vinob/Downloads/Amal/Agents/Langgraph_learning/product_Q_A_chatbot/agent_smart.pdf"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}
    )
    print("📄 PDF Load Response:", pdf_load_response['messages'][-1].content)
    
    # Ask a question about the loaded PDF
    pdf_question_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "What is the main topic discussed in the PDF?"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}
    )
    print("❓ PDF Question Response:", pdf_question_response['messages'][-1].content)
    
    
    print("/n" + "="*60)
    print("🎯 Interactive Testing")
    print("="*60)
    print("You can now test the agents interactively!")
    print("Available commands:")
    print("- Math: 'What's 15 * 3 + 8?'")
    print("- Weather: 'What's the weather in London?'")
    print("- PDF: 'Load the PDF at /path/to/file.pdf' then 'What does the PDF say about...?'")
    print("- Type 'quit' to exit")
    
    # Interactive loop
    while True:
        try:
            user_input = input("/n💬 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
                
            response = await agent.ainvoke(
                {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                },
                config={"callbacks": [ToolCallLogger()]}
            )
            print(f"🤖 Assistant: {response['messages'][-1].content}")
            
        except KeyboardInterrupt:
            print("/n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
 
if __name__ == "__main__":
    asyncio.run(main())