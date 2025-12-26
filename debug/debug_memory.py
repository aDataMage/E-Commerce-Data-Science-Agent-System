import uuid
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.messages import HumanMessage
from main import create_workflow


def debug_memory():
    print("Initializing graph with memory...")
    try:
        graph = create_workflow()
    except Exception as e:
        print(f"Graph initialization failed: {e}")
        return

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"--- Turn 1 (Thread: {thread_id}) ---")
    user_input_1 = "Hi, my name is Alice."
    print(f"User: {user_input_1}")

    try:
        response_1 = graph.invoke(
            {"messages": [HumanMessage(content=user_input_1)]}, config=config
        )
        print(f"Agent: {response_1['messages'][-1].content}")
    except Exception as e:
        print(f"Turn 1 failed: {e}")
        return

    print(f"\n--- Turn 2 (Thread: {thread_id}) ---")
    user_input_2 = "What is my name?"
    print(f"User: {user_input_2}")

    try:
        response_2 = graph.invoke(
            {"messages": [HumanMessage(content=user_input_2)]}, config=config
        )
        agent_response = response_2["messages"][-1].content
        print(f"Agent: {agent_response}")

        if "Alice" in agent_response:
            print("\n✅ SUCCESS: Memory is working!")
        else:
            print("\n❌ FAILURE: Agent did not remember the name.")

    except Exception as e:
        print(f"Turn 2 failed: {e}")

    print(f"\n--- State Inspection (Thread: {thread_id}) ---")
    try:
        current_state = graph.get_state(config)
        messages = current_state.values.get("messages", [])
        print(f"Total messages in history: {len(messages)}")
        for i, msg in enumerate(messages):
            print(f"[{i}] {msg.__class__.__name__}: {msg.content[:50]}...")
    except Exception as e:
        print(f"State inspection failed: {e}")


if __name__ == "__main__":
    debug_memory()
