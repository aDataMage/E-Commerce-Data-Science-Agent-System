"""
Main entry point for the Data Science Agent System.

This module sets up the LangGraph workflow with the Supervisor routing
to specialized agents (A/B Test, Segmentation, General Analytics).
"""

import os
from typing import Dict, Any, Literal
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from src.states.state import AgentState
from src.agents.supervisor import create_supervisor_node, get_next_agent
from src.agents.ab_test_agent import create_ab_test_agent
from src.agents.segmentation_agent import create_segmentation_agent
from src.agents.general_agent import create_general_agent
from src.utils.llm_config import DEFAULT_MODEL


# Load environment variables
load_dotenv(override=True)


def create_workflow(model_name: str = DEFAULT_MODEL) -> StateGraph:
    """
    Create the LangGraph workflow with supervisor routing.

    Args:
        model_name: Gemini model to use for all agents

    Returns:
        Compiled LangGraph workflow
    """
    # Create agent nodes
    supervisor_node = create_supervisor_node(model_name)
    ab_test_node = create_ab_test_agent(model_name)
    segmentation_node = create_segmentation_agent(model_name)
    general_node = create_general_agent(model_name)

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("AB_Agent", ab_test_node)
    workflow.add_node("Segmentation_Agent", segmentation_node)
    workflow.add_node("General_Agent", general_node)

    # Set entry point
    workflow.set_entry_point("Supervisor")

    # Add conditional edges from Supervisor
    workflow.add_conditional_edges(
        "Supervisor",
        get_next_agent,
        {
            "AB_Agent": "AB_Agent",
            "Segmentation_Agent": "Segmentation_Agent",
            "General_Agent": "General_Agent",
            "FINISH": END,
        },
    )

    # All specialized agents route to END after completion
    workflow.add_edge("AB_Agent", END)
    workflow.add_edge("Segmentation_Agent", END)
    workflow.add_edge("General_Agent", END)

    workflow.add_edge("General_Agent", END)

    # Add checkpointer for memory persistence
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)


def run_query(query: str, model_name: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Run a user query through the agent system.

    Args:
        query: User's natural language question
        model_name: Gemini model to use

    Returns:
        Final state containing messages and visualizations
    """
    # Create the workflow
    app = create_workflow(model_name)

    # Initialize state
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query)],
        "next": "",
        "visualizations": [],
    }

    # Run the workflow
    print(f"\n{'=' * 60}")
    print(f"USER QUERY: {query}")
    print("=" * 60)

    final_state = app.invoke(initial_state)

    # Print results
    print(f"\n{'=' * 60}")
    print("RESULTS")
    print("=" * 60)

    for msg in final_state.get("messages", []):
        if hasattr(msg, "content"):
            print(f"\n{msg.__class__.__name__}:")
            print(msg.content[:500] + "..." if len(msg.content) > 500 else msg.content)

    visualizations = final_state.get("visualizations", [])
    if visualizations:
        print(f"\n📊 Generated {len(visualizations)} visualization(s)")
        for i, viz in enumerate(visualizations):
            print(f"  - Visualization {i + 1}: {len(viz)} characters of Plotly JSON")

    return final_state


def main():
    """Main entry point with test query."""
    # Verify API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not set in environment.")
        print("   Create a .env file with: GEMINI_API_KEY=your-key-here")
        print("   Or set it directly: export GEMINI_API_KEY=your-key-here")
        return

    # Test query for A/B test analysis
    test_query = "what is the average order value"

    try:
        result = run_query(test_query)
        print("\n✓ Workflow completed successfully!")
    except Exception as e:
        print(f"\n✗ Error running workflow: {e}")
        raise


if __name__ == "__main__":
    main()
