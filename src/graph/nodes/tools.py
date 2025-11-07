"""Tool execution node."""

from src.graph.state import AgentState
from langchain_core.messages import ToolMessage
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_tool_node(tools):
    """Create tool execution node."""
    
    async def process_tool_calls(state: AgentState) -> AgentState:
        """Process tool calls asynchronously and append results to messages."""
        logger.info("--- Tool Node ---")
        
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.info(f"Executing {len(last_message.tool_calls)} tool call(s)")
            
            tool_messages = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get('name')
                tool_args = tool_call.get('args', {})
                tool_id = tool_call.get('id')
                
                logger.info(f"Calling tool: {tool_name}")
                
                # Find and execute the tool
                for tool in tools:
                    if tool.name == tool_name:
                        try:
                            result = await tool.ainvoke(tool_args)
                            logger.info(f"Tool {tool_name} completed successfully")
                            
                            tool_msg = ToolMessage(
                                content=str(result),
                                tool_call_id=tool_id,
                                name=tool_name
                            )
                            tool_messages.append(tool_msg)
                        except Exception as e:
                            logger.error(f"Tool {tool_name} failed: {e}")
                            tool_msg = ToolMessage(
                                content=f"Error: {str(e)}",
                                tool_call_id=tool_id,
                                name=tool_name
                            )
                            tool_messages.append(tool_msg)
                        break
            
            return {"messages": state["messages"] + tool_messages}
        
        return state
    
    return process_tool_calls