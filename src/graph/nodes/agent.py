"""Agent node that calls the model with tools."""

from src.graph.state import AgentState
from langchain_core.messages import BaseMessage
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_agent_node(model_with_tools):
    """Create agent node with bound tools."""
    
    def agent_node(state: AgentState) -> AgentState:
        """Call the model with tools."""
        logger.info("--- Agent Node ---")
        logger.info(f"Total messages in state: {len(state['messages'])}")
        
        response = model_with_tools.invoke(state["messages"])
        
        logger.info(f"Model response type: {response.__class__.__name__}")
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(f"Tool calls requested: {[tc.get('name') for tc in response.tool_calls]}")
        else:
            logger.info("No tool calls - final answer provided")
        
        return {"messages": state["messages"] + [response]}
    
    return agent_node