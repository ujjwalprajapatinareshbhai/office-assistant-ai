from fastmcp import FastMCP
from core.auth import MyTokenVerifier
from tools.calculator_tools import calculate
from tools.system_tools import system_info  

auth = MyTokenVerifier()

mcp = FastMCP(
    "Utility Server",
    auth=auth
)

#---------------CALCULATOR-------------#

@mcp.tool()
def calculator(expression: str):
    """Evaluate a mathematical expression"""
    return calculate(expression)

#------------------SYSTEM_INFO-------------#

@mcp.tool()
def get_system_info():
    """Return system information."""
    return system_info()



if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8005
    )