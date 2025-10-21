from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize OpenRouter client using LangChain
model = ChatOpenAI(
    model="openai/gpt-oss-20b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


class AgentState(TypedDict):
    messages: list[BaseMessage]


async def main():
    # Initialize MCP client to connect to the weather server
    mcp_client = MultiServerMCPClient(
        {
            "weather": {
                "command": "python",
                "args": ["weather_server.py"],
                "transport": "stdio",
            }
        }
    )

    # Fetch tools from the MCP server
    tools = await mcp_client.get_tools()
    
    logger.info(f"Loaded {len(tools)} tools from MCP server")

    # Create the model with tools bound
    model_with_tools = model.bind_tools(tools)

    # Define the nodes
    def agent_node(state: AgentState) -> AgentState:
        """Call the model with tools."""
        logger.info("--- Agent Node ---")
        
        # Log the current messages
        logger.info(f"Total messages in state: {len(state['messages'])}")
        
        logger.info("Calling model...")
        response = model_with_tools.invoke(state["messages"])
        
        logger.info(f"Model response type: {response.__class__.__name__}")
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(f"Tool calls requested: {[tc.get('name') for tc in response.tool_calls]}")
        else:
            logger.info("No tool calls - final answer provided")
        
        return {"messages": state["messages"] + [response]}

    def should_continue(state: AgentState) -> str:
        """Check if we should continue or end."""
        logger.info("--- Decision Node ---")
        
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.info(f"Decision: Execute {len(last_message.tool_calls)} tool(s)")
            return "tools"
        else:
            logger.info("Decision: End - no tools needed")
            return END

    # Create the state graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    
    # Custom tool node wrapper that handles tool calls properly
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
                            # MCP tools are async, so use ainvoke
                            result = await tool.ainvoke(tool_args)
                            logger.info(f"Tool {tool_name} completed successfully")
                            
                            # Create ToolMessage
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
            
            # Return state with both the original messages and new tool messages
            return {
                "messages": state["messages"] + tool_messages
            }
        
        return state
    
    graph.add_node("tools", process_tool_calls)

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    # Compile the graph
    compiled_graph = graph.compile()

    # Run a test query
    logger.info("")
    logger.info("Starting agent execution")
    
    initial_state = {"messages": [HumanMessage(content="Compare air quality between Tehran and New York")]} 

    logger.info(f"User query: {initial_state['messages'][0].content}")
    
    result = await compiled_graph.ainvoke(initial_state)

    # Print the final response
    logger.info("")
    logger.info("Agent execution complete")
    
    final_message = result["messages"][-1]
    logger.info(f"Total messages: {len(result['messages'])}")
    
    if hasattr(final_message, "content"):
        print("\n" + final_message.content)
    else:
        print("\n" + str(final_message))


asyncio.run(main())