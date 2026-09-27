import asyncio #MCP communication is inherently asynchronous (a client sends a request, then waits for the server's response)
from mcp import Client #counterpart to the server's MCPServer class
#CLient knows how to speak MCP to a server — sending "what tools do you have," 
#sending "call this tool," and correctly parsing responses.(parsing how, see last line)
from mcp_calculator_server import mcp #imports the actual mcp object you already built
async def main() -> None:
    async with Client(mcp) as client: #Creates an actual Client object, connected directly to your mcp server object
#async with is what guarantees that specific object(Client object) gets both connected and properly disconnected, even if an error happens somewhere in between.
        result = await client.call_tool("calculator", {"expression": "0.15 * 200"})
        #actual MCP request being sent — "calculator" is the tool's name (matching exactly what you named your function), 
        #and {"expression": "0.15 * 200"} is the argument, matching your function's parameter name exactly. 
        #await means "pause here until the server actually responds" — this is the real, live MCP conversation happening, client to server.
        print(result.structured_content) #resonse from server is parsed from JSON to  ready-to-use Python object(here .structured_content), if not we hsd have fected ex: ["result"][0] etc

asyncio.run(main())
#starts running your async def main() function — 
#you can't just call main() directly for an async function; 
#asyncio.run(...) is the required way to kick it off.


#run the server script in one shell and then run this client script