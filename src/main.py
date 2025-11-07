"""Main entry point for the weather agent."""

import asyncio
from langchain_core.messages import HumanMessage
from src.tools.weather_mcp import initialize_mcp_client
from src.graph.graph_builder import build_graph
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("Initializing MCP client and loading tools...")
    tools = await initialize_mcp_client()
    
    logger.info("Building agent graph...")
    compiled_graph = build_graph(tools)
    
    logger.info("Starting agent execution")
    
    initial_state = {
        "messages": [HumanMessage(content="Compare air quality between Tehran and New York")]
    }
    
    logger.info(f"User query: {initial_state['messages'][0].content}")
    
    result = await compiled_graph.ainvoke(initial_state)
    
    logger.info("Agent execution complete")
    
    final_message = result["messages"][-1]
    logger.info(f"Total messages: {len(result['messages'])}")
    
    if hasattr(final_message, "content"):
        print("\n" + final_message.content)
    else:
        print("\n" + str(final_message))


if __name__ == "__main__":
    asyncio.run(main())