from fastmcp import FastMCP
from core.auth import MyTokenVerifier

from tools.weather_tools import (
    get_weather,
    get_weather_forecast
)

auth = MyTokenVerifier()

mcp = FastMCP(
    "Weather Server",
    auth=auth
)

@mcp.tool()
def weather_update(city: str):
    """Live Weather updated"""
    return get_weather(city)


@mcp.tool()
def weather_forecast_update(city: str):
    """Weather forecast for tomorrow"""
    return get_weather_forecast(city, days=1)


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8002
    )