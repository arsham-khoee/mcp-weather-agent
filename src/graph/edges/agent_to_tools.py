"""Conditional routing logic for agent to tools decision."""

from src.graph.state import AgentState
from langgraph.graph import END
from src.utils.logger import get_logger

logger = get_logger(__name__)


def should_continue(state: AgentState) -> str:
    """Check if we should continue or end."""
    logger.info("--- Decision Edge ---")
    
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info(f"Decision: Execute {len(last_message.tool_calls)} tool(s)")
        return "tools"
    else:
        logger.info("Decision: End - no tools needed")
        return END