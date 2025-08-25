import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from resources.client_all import test_resource, test_tool, interact_mode

# Server configuration
SERVER_CMD = "python"
SERVER_ARGS = ["turf_server.py"]


async def test_resources(session):
    """Test all MCP resources"""
    return await test_resource(session)
    
    
    

async def test_tools(session):
    """Test MCP tools"""
    return await test_tool(session)
    
    
    
async def interactive_mode(session):
    """Interactive mode for manual testing"""
    return await interact_mode(session)
    


async def main():
    """Main function to test the turf booking MCP server"""
    print("🏟️ Turf Booking System - MCP Client Test")
    print("=" * 60)
    
    # Initialize the server
    server_params = StdioServerParameters(
        command=SERVER_CMD,
        args=SERVER_ARGS,
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()
            
            # List available resources and tools
            print("🔌 Connecting to MCP Server...")
            
            # Get resources
            resources = await session.list_resource_templates()
            print(f"📋 Available Resources: {[r.uriTemplate for r in resources.resourceTemplates]}")
            
            # Get tools  
            tools = await session.list_tools()
            print(f"🛠️ Available Tools: {[tool.name for tool in tools.tools]}")
            
            # Test resources
            await test_resources(session)
            
            # Test tools
            await test_tools(session)
            
            # Interactive mode
            await interactive_mode(session)

if __name__ == "__main__":
    asyncio.run(main())