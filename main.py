# app/main.py
import streamlit as st
from workflow.graph import create_workflow

import initialize
initialize.setup_paths()


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def create_layout():
    st.set_page_config(page_title="SQL & Education Assistant", layout="wide")
    st.title("💬 SQL & Education Assistant")
    st.caption("Ask questions about your database or get educational assistance")

def create_sidebar():
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This assistant can:
        - Answer digital assets related questions
        - Provide analytical insights on real time coin market data
        """)
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

def main():
    init_session_state()
    create_layout()
    create_sidebar()
    
    # Create workflow
    app = create_workflow()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = app.invoke({
                        "question": prompt,
                        "sql_query": "",
                        "query_result": "",
                        "agents": "",
                        "agent_result": ""
                    })
                    
                    st.markdown(response["agent_result"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["agent_result"]
                    })
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
