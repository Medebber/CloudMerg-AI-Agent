# src/database.py
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

def get_vector_db(persist_directory="data/processed/chroma_db"):
    """
    Initializes or loads the Chroma vector database.
    """
    embeddings = OpenAIEmbeddings()
    
    # Ensure the directory exists
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
    
    # We load the DB from the disk using the persistent path
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    return vector_db