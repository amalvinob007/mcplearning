import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test_tools():
    """Simple test to verify MCP tools are working"""
    print("🧪 Testing MCP Tools...")
    
    try:
        # Create client
        client = MultiServerMCPClient({
            "turf": {
                "command": "python",
                "args": ["turf_server.py"],
                "transport": "stdio",
            }
        })
        
        # Get available tools
        tools = await client.get_tools()
        print(f"✅ Found {len(tools)} tools: {[tool.name for tool in tools]}")
        
        # Test get_all_turfs
        print("\n🏟️ Testing get_all_turfs:")
        result = await client.call_tool("get_all_turfs", {})
        if result.content:
            print("✅ Success!")
            print("Result preview:", result.content[0].text[:200] + "..." if len(result.content[0].text) > 200 else result.content[0].text)
        else:
            print("❌ No content returned")
        
        # Test get_all_bookings
        print("\n📅 Testing get_all_bookings:")
        result = await client.call_tool("get_all_bookings", {})
        if result.content:
            print("✅ Success!")
            print("Result preview:", result.content[0].text[:200] + "..." if len(result.content[0].text) > 200 else result.content[0].text)
        else:
            print("❌ No content returned")
            
        await client.aclose()
        print("\n✅ All tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tools())