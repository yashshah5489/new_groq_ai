import os
import chromadb
from chromadb.config import Settings

class ChromaVectorStore:
    def __init__(self, collection_name="financial_docs", persist_directory="chroma_db"):
        # Ensure the persistence directory exists
        os.makedirs(persist_directory, exist_ok=True)
        # Initialize the client with persistence settings
        self.client = chromadb.Client(settings=Settings(persist_directory=persist_directory))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, ids, documents, metadatas=None):
        if metadatas is None:
            metadatas = [{}] * len(documents)
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, query_text: str, n_results: int = 3):
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        return results.get("documents", [[]])[0]
