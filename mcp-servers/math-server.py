from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b:int):
    """This is an addition function that adds 2 numbers together"""
    return a + b 

@mcp.tool()
def subtract(a: int, b: int):
    """Subtraction function"""
    return a - b

@mcp.tool()
def multiply(a: int, b: int):
    """Multiplication function"""
    return a * b

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')