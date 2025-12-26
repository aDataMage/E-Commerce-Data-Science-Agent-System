import os
import uuid
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.messages import HumanMessage
from main import create_workflow


def debug_run():
    print("Initializing graph...")
    try:
        graph = create_workflow()
    except Exception as e:
        print(f"Graph check failed: {e}")
        return

    thread_id = str(uuid.uuid4())
    user_input = "Create a scatter plot showing Customer Lifetime Value vs. Order Frequency for our user segments."
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Invoking graph with input: {user_input}")

    try:
        response = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]}, config=config
        )

        print("\n--- Response ---")
        messages = response.get("messages", [])
        if messages:
            print(messages[-1].content)

        print("\n--- Visualizations ---")
        print(response.get("visualizations", []))

    except Exception as e:
        print(f"Invoke failed: {e}")


if __name__ == "__main__":
    debug_run()
