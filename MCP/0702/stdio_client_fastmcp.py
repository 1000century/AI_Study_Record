from fastmcp import Client


config = {
    "markmap_server": {
        "transport":"stdio",
        "command":"npx",
        "args": ["-y", "@jinzcdev/markmap-mcp-server"],
        "env": {"MARKMAP_DIR": r"C:\Users\Sese\AI_Study_Record\MCP\0702"}
    }
}

client =Client(config)

async def main():
    async with  client:
        tools = await client.list_tools()
        print("Available tools:", tools)
        
        

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())