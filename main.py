# app/main.py
import streamlit as st
from workflow.graph import create_workflow
from typing import Dict
import requests

import initialize
initialize.setup_paths()

def process_via_api(prompt: str) -> Dict:
    api_url = "http://localhost:8000/process" 
    payload = {
        "question": prompt,
        "sql_query": "",
        "query_result": "",
        "agents": "",
        "agent_result": ""
    }
    
    response = requests.post(api_url, json=payload)
    return response.json()



def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def create_layout():
    st.set_page_config(page_title="Intelligent Digital Assets Assistant", layout="wide")
    st.title("💬 Intelligent Digital Assets Assistant")
    st.caption("Ask questions about your digital assets!")

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
                    response = process_via_api(prompt)
                    st.markdown(response["agent_result"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["agent_result"]
                    })
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
