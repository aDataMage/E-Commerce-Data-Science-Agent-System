import os
import uuid
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.messages import HumanMessage
from main import create_workflow


# Mock the setup from app.py
def debug_run():
    print("Initializing graph...")
    try:
        graph = create_workflow()
    except Exception as e:
        print(f"Graph check failed: {e}")
        return

    thread_id = str(uuid.uuid4())
    user_input = (
        "give me a summary of the kind of analysis i can conduct on this dataset"
    )
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Invoking graph with input: {user_input}")

    try:
        # Exact call from app.py
        response = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]}, config=config
        )

        print("\n--- Response Keys ---")
        print(response.keys())

        messages = response.get("messages", [])
        print(f"\n--- Messages ({len(messages)}) ---")
        for i, msg in enumerate(messages):
            print(f"[{i}] Type: {type(msg).__name__}")
            print(
                f"    Content: {repr(getattr(msg, 'content', 'NO CONTENT')[:100])}..."
            )

        print("\n--- Visualizations ---")
        print(response.get("visualizations", []))

    except Exception as e:
        print(f"Invoke failed: {e}")


if __name__ == "__main__":
    debug_run()
