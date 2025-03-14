import streamlit as st
from typing import Dict
import requests
from utils.database import test_db_connection

import initialize
initialize.setup_paths()

def process_via_api(prompt: str) -> Dict:
    api_url = "http://0.0.0.0:8000/process" 
    payload = {
        "question": prompt,
        "sql_query": "",
        "query_result": "",
        "sources": [],
        "web_results": [],
        "summarized_results": [],
        "data": "",
        "agents": "",
        "response": ""
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
        
        # Model selection
        selected_model = st.selectbox(
            "Select your model",
            ('gpt-4o-mini', 'llama3-70b-8192'),
            index=0, # Defailt to llama3-70b-8192
            help="Choose the AI model to use for responses"
            )   
        st.session_state.selected_model = selected_model 
        st.caption(f"{selected_model} is selected")

        # Database connection check
        db, db_connection = test_db_connection()
        if db_connection != 'Error':
            st.success("Database connection successful")
        else:
            st.error("Database connection failed")
        
        # Clear chat history
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
            st.write(message["content"])
            # If message contains visualization code, execute it
            # if "viz_code" in message:
            #     try:
            #         exec(message["viz_code"])
            #     except Exception as e:
            #         st.error(f"Error displaying visualization: {str(e)}")

    # Handle user input
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = process_via_api(prompt)
                    st.write(response["response"])
    
                    # Store both text and visualization in session state
                    message_with_viz = {
                        "role": "assistant",
                        "content": response["response"]
                    }
                    
                    # Add visualization code if present
                    # if "viz_code" in response and response["viz_code"]:
                    #     message_with_viz["viz_code"] = response["viz_code"]
                    #     # Display current visualization
                    #     exec(response["viz_code"])
                    
                    st.session_state.messages.append(message_with_viz)

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
