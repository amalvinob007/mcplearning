# server.py
# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP


mcp = FastMCP("demo-python")



# A dynamic RESOURCE identified by a URI template
@mcp.resource("greeting://Amal")
def greeting(name: str) -> str:
    """Personalized greeting resource"""
    return f"Hello, {name}!"




# A PROMPT template (returns text; SDK wraps it as a prompt message)
@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Ask the model to review code"""
    return f"Please review this {language} code:\n\n```{language}\n{code}\n```"

if __name__ == "__main__":
    mcp.run()  # stdio by default
