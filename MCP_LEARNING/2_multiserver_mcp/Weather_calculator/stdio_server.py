import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.callbacks import AsyncCallbackHandler
import os
from dotenv import load_dotenv
load_dotenv()
 
# Weather API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
 
class ToolCallLogger(AsyncCallbackHandler):
    async def on_tool_start(self, serialized: dict, input: dict, **kwargs) -> None:
        print(f"Tool called: {serialized.get('name')} with input: {input}")
    async def on_tool_end(self, output, **kwargs) -> None:
        print(f"Tool {kwargs.get('name')} output: {output}")
 
async def main():
    # Create MCP client
    client = MultiServerMCPClient(
        {
            "math agent": {
                "command": "python",
                "args": ["C:/Users/amal.vinob/Downloads/Amal/mcp/learning/mcp_agents/new_try_wmulty/math_agent.py"],
                "transport": "stdio",
            },
            "weather agent": {
                "command": "python",
                "args": ["C:/Users/amal.vinob/Downloads/Amal/mcp/learning/mcp_agents/new_try_wmulty/weather_agent.py"],
                "transport": "stdio",
            }
        }
    )
 
    # Get available tools from MCP server
    tools = await client.get_tools() 
    # Universal system prompt
    system_prompt = (
        "You are a versatile assistant capable of handling mathematical expressions and weather queries. "
        "For mathematical expressions, break them down step-by-step, respecting operator precedence (e.g., multiplication before addition). "
        "Use the 'add' tool for addition and the 'multiply' tool for multiplication, ensuring all inputs are integers. "
        "For weather queries, use the 'get_weather' tool with the specified location. "
        "If the query type is unclear, ask for clarification. Always provide clear, step-by-step reasoning."
    )
 
    # Groq LLM setup
    groq_llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,  # Replace with your new Groq API key
        model="llama-3.3-70b-versatile",
    )
 
    # Create ReAct agent
    agent = create_react_agent(
        model=groq_llm,
        tools=tools,
    )
 
    # Test the new query: (3 * 5) + 7
    math_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "What's (3 * 5) + 7?"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}
    )
    print("Math Response:", math_response)
 
    # Test the weather tool
    weather_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "What's the weather in chennai?"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}
    )
    print("Weather Response:", weather_response)
 
if __name__ == "__main__":
    asyncio.run(main())