"""
A/B Test Agent for analyzing campaign performance and statistical significance.
"""

from typing import Dict, Any
from langchain_core.messages import AIMessage, ToolMessage


from src.utils.prompt_loader import load_prompt
from src.utils.llm_config import get_llm, DEFAULT_MODEL
from src.states.state import AgentState
from src.tools.analysis_tools import get_all_tools
from langgraph.prebuilt import create_react_agent


def create_ab_test_agent(model_name: str = DEFAULT_MODEL):
    """
    Create the A/B Test agent node function for LangGraph.

    Args:
        model_name: Gemini model to use

    Returns:
        A function that takes AgentState and returns analysis results
    """
    llm = get_llm(model_name)
    tools = get_all_tools()

    # Load the A/B test prompt
    system_prompt = load_prompt("ab_test_prompt.md")

    # Create the agent using LangGraph's prebuilt React agent
    # This replaces the deprecated AgentExecutor
    agent = create_react_agent(llm, tools, prompt=system_prompt)

    def ab_test_node(state: AgentState) -> Dict[str, Any]:
        """
        Execute A/B test analysis using SQL and Python tools.
        """
        messages = state.get("messages", [])
        # Reset visualizations for this turn to avoid accumulating history
        visualizations = []

        try:
            # Run the agent
            # create_react_agent returns a compiled graph, so we invoke it with state
            result = agent.invoke(
                {"messages": messages}, config={"recursion_limit": 100}
            )

            # The result is the final state, which includes the full message history
            result_messages = result.get("messages", [])

            # Get the final response content
            if result_messages:
                last_msg = result_messages[-1]
                content = last_msg.content
                if isinstance(content, list):
                    # Handle list of content blocks (e.g. from multimodal models)
                    output = " ".join(
                        block.get("text", "")
                        for block in content
                        if isinstance(block, dict) and "text" in block
                    )
                    if not output:  # Fallback if no text blocks
                        output = str(content)
                else:
                    output = str(content)
            else:
                output = "Analysis complete."

            # Extract Generated Images from ToolMessages (Source of Truth)
            import re

            # Check tool messages from the execution
            if result_messages:
                for msg in result_messages:
                    if (
                        isinstance(msg, ToolMessage)
                        and "IMAGE_GENERATED:" in msg.content
                    ):
                        matches = re.findall(
                            r"IMAGE_GENERATED:\s*([^\s]+\.png)", msg.content
                        )
                        if matches:
                            visualizations.extend(matches)

            # Extract any Generated Images from the output (Fallback)
            if "IMAGE_GENERATED:" in output:
                matches = re.findall(r"IMAGE_GENERATED:\s*([^\s]+\.png)", output)
                if matches:
                    for m in matches:
                        if m not in visualizations:
                            visualizations.append(m)

            # Legacy JSON check (can remove if fully switching, but keeping for safety)
            elif "plotly" in output.lower() or '{"data":' in output:
                # ... legacy JSON code ...
                import json

                try:
                    # Look for JSON pattern
                    start_idx = output.find('{"data":')
                    if start_idx != -1:
                        # Find matching closing brace
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
                        # Validate it's proper JSON
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
            error_msg = f"A/B Test analysis error: {str(e)}"
            return {
                "messages": [AIMessage(content=error_msg)],
                "next": "FINISH",
                "visualizations": visualizations,
            }

    return ab_test_node
