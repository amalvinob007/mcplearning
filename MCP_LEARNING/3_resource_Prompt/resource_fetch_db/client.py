# client.py
import asyncio
import os
from pydantic import AnyUrl
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# If your FastMCP server is in server.py and uses mcp.run() (stdio)
SERVER_CMD = "python"
SERVER_ARGS = ["server.py"]

async def main():
    # 1) start the server as a child process over stdio
    server_params = StdioServerParameters(
        command=SERVER_CMD,
        args=SERVER_ARGS,
        # env=os.environ,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 2) handshake
            await session.initialize()

            # -------- PROMPTS ----------
            # list prompts
            prompts = await session.list_prompts()
            print("Prompts:", [p.name for p in prompts.prompts])

            # get/render a prompt (matches @mcp.prompt() def code_review(...) from your server)
            prompt = await session.get_prompt(
                "code_review",
                arguments={"language": "python", "code": "def add(a,b): return a+b"},
            )
            # prompt.messages is what you'd feed to your model
            for msg in prompt.messages:
                if isinstance(msg.content, types.TextContent):
                    print("Prompt message:", msg.content.text)
            print()

            # -------- RESOURCES ----------
            # list resources
            resources = await session.list_resource_templates()
            print("Resources:", [r.uriTemplate for r in resources.resourceTemplates])
            print()

            # Test existing greeting resource
            print("=== GREETING RESOURCE ===")
            res = await session.read_resource("greeting://Amal")
            print("Greeting content:", res.contents[0].text)
            print()

            # Test new database resources
            print("=== DATABASE RESOURCES ===")
            
            # 1. All employees (static)
            print("1. All Employees:")
            res = await session.read_resource("db://employees/all")
            print(res.contents[0].text)
            print()
            
            # 2. Employees by department (dynamic)
            print("2. Engineering Department:")
            res = await session.read_resource("db://employees/department/Engineering")
            print(res.contents[0].text)
            print()
            
            print("3. HR Department:")
            res = await session.read_resource("db://employees/department/HR")
            print(res.contents[0].text)
            print()
            
            # 3. Employee by ID (dynamic)
            print("4. Employee ID 3:")
            res = await session.read_resource("db://employees/id/3")
            print(res.contents[0].text)
            print()
            
            # 4. Test invalid ID
            print("5. Invalid Employee ID (999):")
            res = await session.read_resource("db://employees/id/999")
            print(res.contents[0].text)

if __name__ == "__main__":
    asyncio.run(main())