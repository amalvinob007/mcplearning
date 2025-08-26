import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.callbacks import AsyncCallbackHandler
 
# Callback to log tool calls for debugging
class ToolCallLogger(AsyncCallbackHandler):
    async def on_tool_start(self, serialized: dict, input: dict, **kwargs) -> None:
        print(f"Tool called: {serialized.get('name')} with input: {input}")
 
async def main():
    # Create MCP client
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["C:/Users/amal.vinob/Downloads/Amal/mcp/learning/mcp_agents/new_try/agent_tool.py"],
                "transport": "stdio",
            }
        }
    )
 
    # Get available tools from MCP server
    tools = await client.get_tools()
 
    # Groq LLM setup with system prompt
    system_prompt = (
        "You are a math assistant. For expressions like (a + b) x c, first compute the addition (a + b) using the 'add' tool, "
        "then use the result with the 'multiply' tool to multiply by c. Ensure all tool inputs are integers."
    )
    groq_llm = ChatGroq(
        groq_api_key="",  # Replace with actual API key
        model="llama-3.3-70b-versatile",
        # Pass system prompt as part of the messages in the invoke call
    )
 
    # Create ReAct agent with Groq + MCP tools
    agent = create_react_agent(
        model=groq_llm,
        tools=tools,
    )
 
    # Run the agent with the system prompt included in the messages
    math_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "what's (3 + 5) x 12?"}
            ]
        },
        config={"callbacks": [ToolCallLogger()]}  # Add callback for debugging
    )
    print("Response:", math_response)
 
if __name__ == "__main__":

    asyncio.run(main())
