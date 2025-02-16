# agents/advisor.py
from models import State
from config import llm, ADVISOR_SYS_PROMPT
from langchain.prompts.chat import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Initialize FAISS index
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
index_file = "data/index.faiss"

def advisor_llm(state: State):
    """Retrieves relevant documents from the local FAISS vector store and generates a response."""
    question = state["question"]

    # Check if FAISS index exists
    if not os.path.exists(index_file):
        return {"agent_result": "No data available. Please upload a PDF first."}

    # Load the FAISS index
    index = faiss.read_index(index_file)

    # Generate embeddings for the user query
    query_vector = embedding_model.encode([question])
    query_vector = np.array(query_vector, dtype=np.float32)

    # Perform similarity search
    k = 3  # retrieve top 3 relevant chunks
    distances, indices = index.search(query_vector, k)

    # Retrieve the corresponding text chunks
    with open("data/chunks.txt", "r") as f:
        text_chunks = f.readlines()

    retrieved_chunks = [text_chunks[i].strip() for i in indices[0] if i < len(text_chunks)]

    # Combine retrieved chunks into context
    context = "\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."

    # Generate the response using LangChain
    system = ADVISOR_SYS_PROMPT
    human = f"Context: {context}\n\nUser Query: {question}"

    advisor_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human),
    ])

    response = advisor_prompt | llm
    state["agent_result"] = response.invoke({})

    return state