import pdfplumber
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

from langchain.tools import QuerySQLDatabaseTool
from models import State
from config import llm, ADVISOR_SYS_PROMPT
from langchain_community.utilities import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Initialize SQL Database
db = SQLDatabase.from_uri("postgresql://postgres:postgres@localhost:5432", include_tables=["cryptocurrencies", "market_data"])

# Initialize Embedding Model for FAISS
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
index_file = "data/index.faiss"


# Execute SQL Queries
def execute_query(state: State):
    """Execute an SQL query using the database."""
    try:
        execute_query_tool = QuerySQLDatabaseTool(db=db)
        result = execute_query_tool.invoke(state["sql_query"])
        state["query_result"] = result
        return state
    except Exception as e:
        raise ValueError(f"Error executing query: {str(e)}")


# Generate Answers Based on SQL Results
def generate_answer(state: State):
    """Generate a human-readable answer based on SQL query and result."""
    question = state["question"]
    sql = state["sql_query"]
    result = state["query_result"]

    generate_prompt = ChatPromptTemplate.from_messages([
        (
            "human",
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {question}\n'
            f'SQL Query: {sql}\n'
            f'SQL Result: {result}\n\n'
            "If you find any errors or empty results, simply say: 'I'm sorry, I cannot help you with that.' "
            "Never mention how you arrived at the answer."
        ),
    ])

    human_response = generate_prompt | llm | StrOutputParser()
    answer = human_response.invoke({})
    state["agent_result"] = answer
    return state


# Extract Text and Store in FAISS
def extract_and_store_text(pdf_path):
    """Extracts text from a PDF and stores embeddings in a FAISS vector database."""
    # Step 1: Extract text from PDF
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if not text:
        raise ValueError("No text found in the PDF. Please provide a valid document.")

    # Step 2: Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(text)

    # Step 3: Generate embeddings for the text chunks
    embeddings = embedding_model.encode(chunks)
    embeddings = np.array(embeddings, dtype=np.float32)

    # Step 4: Create and store the FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save the FAISS index to disk
    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, index_file)

    # Save text chunks for retrieval
    with open("data/chunks.txt", "w") as f:
        for chunk in chunks:
            f.write(chunk + "\n")

    print("PDF processed and embeddings stored successfully.")


# Retrieve Relevant Chunks from FAISS
def retrieve_relevant_chunks(query, top_k=3):
    """Retrieve the top-k most relevant text chunks from the FAISS vector store."""
    # Ensure the FAISS index exists
    if not os.path.exists(index_file):
        raise FileNotFoundError("The FAISS index file does not exist. Please upload and process a PDF first.")

    # Load the FAISS index
    index = faiss.read_index(index_file)

    # Generate the query embedding
    query_vector = embedding_model.encode([query])
    query_vector = np.array(query_vector, dtype=np.float32)

    # Perform similarity search
    distances, indices = index.search(query_vector, top_k)

    # Retrieve the corresponding text chunks
    with open("data/chunks.txt", "r") as f:
        text_chunks = f.readlines()

    # Fetch the retrieved chunks
    retrieved_chunks = [text_chunks[i].strip() for i in indices[0] if i < len(text_chunks)]

    return retrieved_chunks


# Generate Response Using Retrieved Context
def generate_rag_response(state: State):
    """Generate a response by retrieving context from FAISS and using the LLM."""
    question = state["question"]

    # Retrieve relevant text chunks
    retrieved_chunks = retrieve_relevant_chunks(question)
    context = "\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."

    # Construct the chat prompt with retrieved context
    advisor_prompt = ChatPromptTemplate.from_messages([
        ("system", ADVISOR_SYS_PROMPT),
        ("human", f"Context: {context}\n\nUser Query: {question}")
    ])

    # Generate response using LangChain
    response = advisor_prompt | llm
    state["agent_result"] = response.invoke({})

    return state
