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
            # prompt.messages is what you’d feed to your model
            for msg in prompt.messages:
                if isinstance(msg.content, types.TextContent):
                    print("Prompt message:", msg.content.text)

            # -------- RESOURCES ----------
            # list resources
            resources = await session.list_resources()
            print("Resources:", [r.uri for r in resources.resources])

            # read a resource by URI (matches @mcp.resource('greeting://{name}'))
            # res = await session.read_resource(AnyUrl("greeting://Lidhiya"))
            # for block in res.contents:
            #     if isinstance(block, types.TextContent):
            #         print("Resource content:", block.text)
            # names = ["Amal", "Vinob"]
            # for name in names:
            #     res = await session.read_resource(AnyUrl(f"greeting://{name}"))
            #     for block in res.contents:
            #         if isinstance(block, types.TextContent):
            #             print(f"{name} → {block.text}")


if __name__ == "__main__":
    asyncio.run(main())
