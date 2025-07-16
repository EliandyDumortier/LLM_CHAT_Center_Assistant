import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChromaDBClient:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client with persistent storage"""
        try:
            # Create ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory,
                settings=ChromaSettings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
            
            # Initialize embedding function using sentence transformers
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                embedding_function=self.embedding_function
            )
            
            logger.info(f"ChromaDB initialized successfully with collection: {settings.chroma_collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def get_collection(self):
        """Get the current collection"""
        if self.collection is None:
            self._initialize_client()
        return self.collection
    
    def add_documents(self, documents: list, metadatas: list, ids: list):
        """Add documents to the collection"""
        try:
            collection = self.get_collection()
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to collection")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    def query_documents(self, query_text: str, n_results: int = 5):
        """Query documents from the collection"""
        try:
            collection = self.get_collection()
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            return None
    
    def reset_collection(self):
        """Reset the collection (for testing purposes)"""
        try:
            if self.client and self.collection:
                self.client.delete_collection(settings.chroma_collection_name)
                self.collection = self.client.create_collection(
                    name=settings.chroma_collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info("Collection reset successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False

# Global client instance
chroma_client = ChromaDBClient()