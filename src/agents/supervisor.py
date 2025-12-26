"""
Supervisor Agent for routing user queries to specialized agents.
Uses LLM to analyze the query and determine the appropriate handler.
"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.utils.prompt_loader import load_prompt, get_schema_string
from src.utils.llm_config import get_llm, DEFAULT_MODEL
from src.states.state import AgentState


def create_supervisor_node(model_name: str = DEFAULT_MODEL):
    """
    Create the supervisor node function for LangGraph.

    Args:
        model_name: Gemini model to use for routing decisions

    Returns:
        A function that takes AgentState and returns updated state with routing decision
    """
    llm = get_llm(model_name)

    def supervisor_node(state: AgentState) -> Dict[str, Any]:
        """
        Analyze user query and route to appropriate agent.

        Returns updated state with 'next' field set to one of:
        - "AB_Agent"
        - "Segmentation_Agent"
        - "General_Agent"
        - "FINISH"
        """
        # Get the database schema for context
        try:
            schema = get_schema_string()
        except Exception:
            schema = "Schema unavailable - database not initialized"

        # Load the supervisor prompt with schema injected
        system_prompt = load_prompt("supervisor_prompt.md", schema=schema)

        # Get the last user message
        messages = state.get("messages", [])
        if not messages:
            return {
                "next": "FINISH",
                "messages": [AIMessage(content="No query provided.")],
            }

        # Build conversation for LLM
        # Include system prompt and all messages
        llm_messages = [SystemMessage(content=system_prompt)] + messages

        # Get routing decision
        response = llm.invoke(llm_messages)

        # Parse the JSON response
        try:
            # Extract content, handling potential list format (multimodal)
            content = response.content
            if isinstance(content, list):
                content = " ".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and "text" in block
                )

            # Ensure content is a string
            content = str(content)
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            decision = json.loads(content.strip())
            next_agent = decision.get("next", "FINISH")
            reasoning = decision.get("reasoning", "")
            finish_message = decision.get("message", "")

            # Validate next agent
            valid_agents = ["AB_Agent", "Segmentation_Agent", "General_Agent", "FINISH"]
            if next_agent not in valid_agents:
                next_agent = "General_Agent"  # Default fallback

            # Build response message
            if next_agent == "FINISH":
                response_content = finish_message or "Analysis not supported."
            else:
                response_content = f"Routing to {next_agent}. Reason: {reasoning}"

            return {
                "next": next_agent,
                "messages": [AIMessage(content=response_content)],
            }

        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: try to infer from raw response
            content = response.content
            if isinstance(content, list):
                content = " ".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and "text" in block
                )
            content_lower = str(content).lower()

            if "ab_agent" in content_lower or "a/b" in content_lower:
                next_agent = "AB_Agent"
            elif "segmentation" in content_lower or "cluster" in content_lower:
                next_agent = "Segmentation_Agent"
            elif "general" in content_lower:
                next_agent = "General_Agent"
            else:
                next_agent = "General_Agent"  # Default

            return {
                "next": next_agent,
                "messages": [AIMessage(content=f"Routing to {next_agent}")],
            }

    return supervisor_node


def get_next_agent(state: AgentState) -> str:
    """
    Router function for LangGraph conditional edges.
    Returns the next agent name from state.
    """
    return state.get("next", "FINISH")
