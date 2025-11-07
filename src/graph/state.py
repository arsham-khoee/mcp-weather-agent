from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State for the weather agent workflow."""
    messages: list[BaseMessage]