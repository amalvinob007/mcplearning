# File: calculator_server.py
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Adds two integers.
    
    Args:
        a (int): The first integer.
        b (int): The second integer.
    
    Returns:
        int: The sum of the two integers.
    """
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiplies two integers.
    
    Args:
        a (int): The first integer.
        b (int): The second integer.
    
    Returns:
        int: The product of the two integers.
    """
    return a * b

# This is the crucial part that actually runs the server
if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run())