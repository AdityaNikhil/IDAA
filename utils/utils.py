import pdfplumber
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter
import os

# Initialize the FAISS vector store
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# File paths
index_file = "index.faiss"
chunks_file = "chunks.txt"

# Cryptocurrency-related keywords (need to add more terms if possible)
CRYPTO_KEYWORDS = {"crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain", "web3",
                   "decentralized", "mining", "token", "NFT", "stablecoin", "defi", "ledger"}


def extract_and_store_text(pdf_path):
    """Extract and store PDF text if it matches the cryptocurrency topic."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Check for cryptocurrency-related keywords
    if not any(keyword in text.lower() for keyword in CRYPTO_KEYWORDS):
        raise ValueError("PDF content does not match the required topic: Cryptocurrency")

    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(text)

    # Generate embeddings
    embeddings = embedding_model.encode(chunks)
    embeddings = np.array(embeddings, dtype=np.float32)

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save the FAISS index
    faiss.write_index(index, index_file)

    # Save the text chunks
    with open(chunks_file, "w") as f:
        for chunk in chunks:
            f.write(chunk + "\n")

    print("Cryptocurrency-related PDF processed successfully.")


def retrieve_relevant_chunks(query, top_k=3):
    """Retrieve the top-k most relevant text chunks from FAISS."""
    if not os.path.exists(index_file):
        print("FAISS index not found. Attempting to create index from PDF...")
        try:
            pdf_path = 'pdfs/Mastering-Crypto-Day-Trading-From-Blockchain-Basics-to-Profits.pdf'
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
            extract_and_store_text(pdf_path)
            print("Successfully created FAISS index.")
        except ValueError as ve:
            raise ValueError(f"Error processing PDF: {ve}")
        except Exception as e:
            raise Exception(f"Failed to create FAISS index: {e}")

    try:
        # Load FAISS index
        index = faiss.read_index(index_file)
    except Exception as e:
        raise Exception(f"Error reading FAISS index: {e}")

    if not os.path.exists(chunks_file):
        raise FileNotFoundError("Text chunks file not found. Please process the PDF again.")

    # Generate the query embedding
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding, dtype=np.float32)

    # Search the FAISS index
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve the corresponding text chunks
    try:
        with open(chunks_file, "r") as f:
            text_chunks = f.readlines()
    except Exception as e:
        raise Exception(f"Error reading text chunks: {e}")

    retrieved_chunks = [text_chunks[i].strip() for i in indices[0] if i < len(text_chunks)]
    
    if not retrieved_chunks:
        print("Warning: No relevant chunks found for the query.")
        
    return retrieved_chunks