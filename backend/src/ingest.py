import os
from dotenv import load_dotenv

# 1. Mistral-specific Brain
from langchain_mistralai import MistralAIEmbeddings

# 2. Reading & Cutting Tools
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 3. Storage (Use the specific chroma package)
from langchain_chroma import Chroma

load_dotenv()

def run_ingestion():
    # Use absolute paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_path = os.path.join(base_path, "data", "raw")
    persist_directory = os.path.join(base_path, "data", "processed", "chroma_db")

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Error: MISTRAL_API_KEY not found in .env")
        return

    if not os.path.exists(raw_data_path):
        print(f"Folder not found: {raw_data_path}")
        return

    # 1. Load PDFs
    documents = []
    print("Loading PDFs...")
    for file in os.listdir(raw_data_path):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(raw_data_path, file))
            documents.extend(loader.load())

    # 2. Chunk Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    # 3. Mistral Embeddings (Matches your Engine)
    embeddings = MistralAIEmbeddings(
    model="mistral-embed", 
    mistral_api_key=api_key
)

    # 4. Save to ChromaDB
    print(f"Creating database at {persist_directory}...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print(f"Success! Ingested {len(chunks)} chunks using Mistral Embeddings.")

if __name__ == "__main__":
    run_ingestion()