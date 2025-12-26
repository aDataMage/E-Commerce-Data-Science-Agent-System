"""
General Analytics Agent for SQL aggregations and basic metrics.
"""

from typing import Dict, Any
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from src.utils.prompt_loader import load_prompt
from src.utils.llm_config import get_llm, DEFAULT_MODEL
from src.states.state import AgentState
from src.tools.analysis_tools import get_all_tools


def create_general_agent(model_name: str = DEFAULT_MODEL):
    """
    Create the General Analytics agent node function for LangGraph.

    Args:
        model_name: Gemini model to use

    Returns:
        A function that handles general analytics queries
    """
    llm = get_llm(model_name)
    tools = get_all_tools()

    # Load the general prompt
    system_prompt = load_prompt("general_prompt.md")

    # Create the agent using LangGraph's prebuilt React agent
    agent = create_react_agent(llm, tools, prompt=system_prompt)

    def general_node(state: AgentState) -> Dict[str, Any]:
        """
        Execute general analytics using SQL and Python tools.
        """
        messages = state.get("messages", [])
        # Reset visualizations for this turn to avoid accumulating history
        visualizations = []

        try:
            # Run the agent
            result = agent.invoke(
                {"messages": messages}, config={"recursion_limit": 100}
            )

            result_messages = result.get("messages", [])

            if result_messages:
                last_msg = result_messages[-1]
                content = last_msg.content
                if isinstance(content, list):
                    output = " ".join(
                        block.get("text", "")
                        for block in content
                        if isinstance(block, dict) and "text" in block
                    )
                    if not output:
                        output = str(content)
                else:
                    output = str(content)
            else:
                output = "Analysis complete."

            # Extract Generated Images from ToolMessages (Source of Truth)
            import re

            for msg in result_messages:
                if isinstance(msg, ToolMessage) and "IMAGE_GENERATED:" in msg.content:
                    matches = re.findall(
                        r"IMAGE_GENERATED:\s*([^\s]+\.png)", msg.content
                    )
                    if matches:
                        visualizations.extend(matches)

            # Also check final output just in case (fallback)
            if "IMAGE_GENERATED:" in output:
                matches = re.findall(r"IMAGE_GENERATED:\s*([^\s]+\.png)", output)
                if matches:
                    # Avoid duplicates
                    for m in matches:
                        if m not in visualizations:
                            visualizations.append(m)

            # Legacy JSON check
            elif "plotly" in output.lower() or '{"data":' in output:
                import json

                try:
                    start_idx = output.find('{"data":')
                    if start_idx != -1:
                        # ... simplistic extraction ...
                        brace_count = 0
                        end_idx = start_idx
                        for i, char in enumerate(output[start_idx:]):
                            if char == "{":
                                brace_count += 1
                            elif char == "}":
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = start_idx + i + 1
                                    break
                        json_str = output[start_idx:end_idx]
                        json.loads(json_str)
                        visualizations = visualizations + [json_str]
                except (json.JSONDecodeError, ValueError):
                    pass

            return {
                "messages": [AIMessage(content=output)],
                "next": "FINISH",
                "visualizations": visualizations,
            }

        except Exception as e:
            error_msg = f"General analytics error: {str(e)}"
            return {
                "messages": [AIMessage(content=error_msg)],
                "next": "FINISH",
                "visualizations": visualizations,
            }

    return general_node
