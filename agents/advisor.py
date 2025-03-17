from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from models import State
from utils.utils import retrieve_relevant_chunks
from config import ADVISOR_LLM_PROMPT
import os


def advisor_agent(state: State):
    """Generate a response from the advisor agent using FAISS-based context and Groq API."""
    try:
        # Retrieve context
        retrieved_chunks = retrieve_relevant_chunks(state["question"])
        context = "\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."

        # Construct the chat prompt with the strict cryptocurrency-only system prompt
        advisor_prompt = ChatPromptTemplate.from_messages([
            ("system", ADVISOR_LLM_PROMPT),
            ("human", f"Context: {context}\n\nUser Query: {state["question"]}")
        ])

        # Initialize Groq LLM with the correct model
        groq_api_key = os.getenv("GROQ_API_KEY")
        llm = ChatGroq(model="mixtral-8x7b-32768", api_key=groq_api_key)

        # Generate response using LangChain LLM
        response = advisor_prompt | llm
        result = response.invoke({})

        # Ensure the response is not mixed and only provides relevant output
        response_text = result.content.strip()

        state["response"] = response_text

        return state

    except Exception as e:
        return f"An error occurred: {e}"
