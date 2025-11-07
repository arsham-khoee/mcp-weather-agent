"""Main graph builder."""

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from src.graph.state import AgentState
from src.graph.nodes.agent import create_agent_node
from src.graph.nodes.tools import create_tool_node
from src.graph.edges import should_continue
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_graph(tools):
    """Build the agent graph."""
    
    # Initialize model from configuration
    model = ChatOpenAI(
        model=settings.model_config.model_name,
        base_url=settings.model_config.base_url,
        api_key=settings.model_config.api_key,
        temperature=settings.model_config.temperature,
        max_tokens=settings.model_config.max_tokens,
    )
    
    model_with_tools = model.bind_tools(tools)
    
    # Create graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("agent", create_agent_node(model_with_tools))
    graph.add_node("tools", create_tool_node(tools))
    
    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")
    
    return graph.compile()