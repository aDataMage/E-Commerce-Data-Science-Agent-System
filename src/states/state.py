"""
State definitions for the Data Science Agent System.
Defines the AgentState TypedDict used across all agents.
"""
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Shared state across all agents in the LangGraph workflow.
    
    Attributes:
        messages: List of conversation messages (HumanMessage, AIMessage, etc.)
        next: The next agent to route to (or "FINISH" to end)
        visualizations: Accumulated Plotly JSON strings for frontend rendering
    """
    messages: Annotated[List[BaseMessage], operator.add]
    next: str
    visualizations: List[str]
