# MCP is a standardized way for an AI agent (a "client") to discover
# and call tools. Before MCP, every framework (LangChain, OpenAI, etc.)
# had its own incompatible way of defining a tool. MCP means: build
# the tool ONCE, as an MCP server, and ANY MCP-compatible client can
# use it - no need to rewrite it for every different framework.

from mcp.server.mcpserver import MCPServer

mcp=MCPServer("calculator-server") #creates an instance(object) of the FastMCP class,
#Think of this as creating your MCP server itself, but as a plain Python object, 
#sitting in memory, not yet actually running or listening for anything.

@mcp.tool() #specifically tells your mcp object: "remember this next function as one of my available tools."
def calculator(expression: str) -> str:
    """Evaluates a basic math expression, e.g. '15% of 200' should be passed as '0.15 * 200'."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run() #makes your server actually start listening for incoming MCP requests, 
              #using all the tool information registered above it via the @mcp.tool() decorator.