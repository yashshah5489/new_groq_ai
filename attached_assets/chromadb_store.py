import os
import logging
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    def __init__(self, collection_name="financial_docs", persist_directory="chroma_db"):
        """Initialize ChromaDB with proper settings and embedding function"""
        try:
            # Ensure the persistence directory exists
            os.makedirs(persist_directory, exist_ok=True)

            # Initialize the client with persistence settings
            self.client = chromadb.Client(
                Settings(
                    persist_directory=persist_directory,
                    anonymized_telemetry=False
                )
            )

            # Use sentence-transformers for better embeddings
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )

            # Get or create collection with embedding function
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"Successfully initialized ChromaDB collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise

    def add_documents(self, ids, documents, metadatas=None):
        """Add documents to the vector store"""
        try:
            if metadatas is None:
                metadatas = [{}] * len(documents)

            # Ensure all inputs are lists and have the same length
            if not all(isinstance(x, list) for x in [ids, documents]) or \
               not len(ids) == len(documents) == len(metadatas):
                raise ValueError("ids, documents, and metadatas must be lists of equal length")

            self.collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise

    def query(self, query_text: str, n_results: int = 3):
        """Query the vector store with better error handling and logging"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )

            # Extract and return only the documents
            documents = results.get("documents", [[]])[0]
            logger.info(f"Successfully queried ChromaDB. Found {len(documents)} results")
            return documents
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise

    def get_collection_stats(self):
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise