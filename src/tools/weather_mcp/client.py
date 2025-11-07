"""MCP client initialization and tool loading."""

from langchain_mcp_adapters.client import MultiServerMCPClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def initialize_mcp_client():
    """Initialize MCP client and load weather tools."""
    mcp_client = MultiServerMCPClient(
        {
            "weather": {
                "command": "python",
                "args": ["-m", "src.tools.weather_mcp.server"],
                "transport": "stdio",
            }
        }
    )
    
    tools = await mcp_client.get_tools()
    logger.info(f"Loaded {len(tools)} tools from MCP server")
    
    return tools