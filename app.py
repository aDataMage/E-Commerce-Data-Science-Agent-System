import streamlit as st
import json
import plotly.io as pio
import uuid
import os
from langchain_core.messages import HumanMessage
from main import create_workflow

# Page Config
st.set_page_config(
    page_title="Agentic Data Analyst", layout="wide", initial_sidebar_state="expanded"
)

# --- Core Logic & State Management ---


@st.cache_resource
def get_graph():
    """
    Initialize and cache the LangGraph workflow.
    This prevents reloading the heavy agent logic on every interaction.
    """
    return create_workflow()


# Initialize graph
try:
    graph = get_graph()
except Exception as e:
    st.error(f"Failed to load agent workflow: {e}")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

# --- Sidebar ---

with st.sidebar:
    st.title("System Monitor")

    # DB Status Check
    db_path = "ecommerce.db"
    if os.path.exists(db_path):
        st.success("🟢 DB Connected")
    else:
        st.error("🔴 DB Missing")

    st.markdown("---")

    # Reset Conversation
    if st.button("Reset Conversation", type="primary"):
        st.session_state["messages"] = []
        st.session_state["thread_id"] = str(uuid.uuid4())
        st.rerun()

    st.markdown("---")
    st.caption(f"Thread ID:\n{st.session_state['thread_id']}")

# --- Main Chat Area ---

st.title("Agentic Data Analyst 🤖")

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        # Handle list content (legacy/multimodal support)
        content = msg["content"]
        if isinstance(content, list):
            # Extract text from blocks
            text_parts = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    text_parts.append(block["text"])
                elif isinstance(block, str):
                    text_parts.append(block)
            content = " ".join(text_parts)

        st.markdown(content)

        # Display cached visualizations if any exist for this message
        if "visualizations" in msg and msg["visualizations"]:
            for viz in msg["visualizations"]:
                try:
                    # Check if it's a file path (static image)
                    if isinstance(viz, str) and viz.strip().endswith(".png"):
                        import os

                        if os.path.exists(viz):
                            st.image(viz, caption="Analysis Visualization")
                            with open(viz, "rb") as file:
                                st.download_button(
                                    label="Download Plot",
                                    data=file,
                                    file_name=os.path.basename(viz),
                                    mime="image/png",
                                    key=f"history_dl_{viz}",
                                )
                        else:
                            st.warning(f"Image generated but file not found: {viz}")
                    else:
                        # Fallback for old Plotly JSON
                        fig = pio.from_json(viz)
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    # Silent fail or small warning for history
                    st.caption(f"Cannot render chart: {e}")

# --- Interaction Loop ---

if user_input := st.chat_input("Ask about your data..."):
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Append to state
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # 2. Processing
    response = None
    with st.spinner("Analyzing data..."):
        try:
            # Config for LangGraph to track state
            config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

            # Invoke Graph
            response = graph.invoke(
                {"messages": [HumanMessage(content=user_input)]}, config=config
            )
        except Exception as e:
            st.error(f"Analysis Failed: {e}")
            print(f"Error during graph invocation: {e}")

    # 3. Response Handling (Outside Spinner)
    if response:
        messages = response.get("messages", [])
        visualizations = response.get("visualizations", [])

        # Find the last AI message
        ai_content = "No response generated."

        # Search backwards for the last AIMessage
        for msg in reversed(messages):
            if msg.type == "ai":
                ai_content = msg.content
                break

        # Display AI Message
        with st.chat_message("assistant"):
            st.markdown(ai_content)

        if visualizations:
            for viz in visualizations:
                try:
                    # Check if it's a file path (static image)
                    if isinstance(viz, str) and viz.strip().endswith(".png"):
                        import os

                        if os.path.exists(viz):
                            st.image(viz, caption="Analysis Visualization")
                            with open(viz, "rb") as file:
                                st.download_button(
                                    label="Download Plot",
                                    data=file,
                                    file_name=os.path.basename(viz),
                                    mime="image/png",
                                    key=f"live_dl_{viz}",
                                )
                        else:
                            st.warning(f"Image generated but file not found: {viz}")
                    else:
                        # Fallback for old Plotly JSON
                        fig = pio.from_json(viz)
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error rendering visualization: {e}")

        # Append AI response to state for history with visualizations
        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": ai_content,
                "visualizations": visualizations,
            }
        )
