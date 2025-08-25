# File: calculator_client.py
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def main():
    print("Starting client...")
    
    # Define how to start the server
    server_params = StdioServerParameters(
        command="python",
        args=["calculator_server.py"]
    )
    
    print("Connecting to server...")
    try:
        # Use the stdio_client context manager properly
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("Server started, creating session...")
            
            # Create and initialize the client session
            async with ClientSession(read_stream, write_stream) as session:
                print("Session created, initializing...")
                
                
                # Initialize the session
                init_result = await session.initialize()
                # print(f"Session initialized: {init_result}")

                print("Protocol version:", init_result.protocolVersion)
                print(init_result.capabilities)
                print("Server info:", init_result.serverInfo)

                
                print("Listing tools...")
                # List available tools
                tools_result = await session.list_tools()
                print("Available tools:", tools_result.tools if hasattr(tools_result, 'tools') else tools_result)
                
                print("Calling add tool...")
                # Call the 'add' tool
                result1 = await session.call_tool("add", {"a": 5, "b": 10})
                print("Result of add(5, 10):", result1)
                
                print("Calling multiply tool...")
                # Call the 'multiply' tool
                result2 = await session.call_tool("multiply", {"a": 3, "b": 7})
                print("Result of multiply(3, 7):", result2)
                
                print("All operations completed successfully!")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())