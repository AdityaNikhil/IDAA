import streamlit as st
from workflow.graph import workflow  # Import the compiled workflow
from utils.database import extract_and_store_text, retrieve_relevant_chunks
import initialize
import os

# Run initialization tasks if needed
initialize.setup_paths()


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pdf_processed" not in st.session_state:
        st.session_state.pdf_processed = False


def create_layout():
    """Set up the main interface layout."""
    st.set_page_config(page_title="Digital Assets Assistant", layout="wide")
    st.title("Intelligent Digital Assets Assistant")
    st.caption("Ask questions about digital assets in real-time or get educational assistance.")


def create_sidebar():
    """Create the sidebar with app information."""
    with st.sidebar:
        st.header("About")
        st.markdown("""
        **This assistant can:**  
        - Answer questions about digital assets  
        - Provide analytical insights  
        - Offer educational guidance  
        - Retrieve information from uploaded PDFs  
        """)
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


def handle_pdf_upload():
    """Handles PDF file upload and processing."""
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file is not None:
        # Save the uploaded file locally
        pdf_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process the PDF and store embeddings using FAISS
        try:
            extract_and_store_text(pdf_path)
            st.session_state.pdf_processed = True
            st.success(f"PDF '{uploaded_file.name}' uploaded and processed successfully!")
        except Exception as e:
            st.error(f"Failed to process the PDF: {e}")


def display_chat_history():
    """Display the chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_user_input(app):
    """Process the user input and interact with the agent."""
    if prompt := st.chat_input("💬 What would you like to know?"):
        # Display the user's message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                try:
                    # Check FAISS vector store for context
                    retrieved_chunks = retrieve_relevant_chunks(prompt)
                    if retrieved_chunks:
                        context = "\n".join(retrieved_chunks)
                        st.markdown(f"**Context Retrieved:**\n{context}")

                    # Invoke the workflow with the user's question
                    response = app.run({
                        "question": prompt,
                        "sql_query": "",
                        "query_result": "",
                        "agents": "",
                        "agent_result": ""
                    })

                    # Display the assistant's response
                    answer = response.get("agent_result", "No response generated.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


def main():
    """Main Streamlit application logic."""
    init_session_state()
    create_layout()
    create_sidebar()

    # Step 1: PDF Upload
    handle_pdf_upload()

    # Step 2: Display chat history
    display_chat_history()

    # Step 3: Process user input if PDF is processed
    if st.session_state.pdf_processed:
        process_user_input(workflow)
    else:
        st.warning("Please upload and process a PDF before asking questions.")


if __name__ == "__main__":
    main()