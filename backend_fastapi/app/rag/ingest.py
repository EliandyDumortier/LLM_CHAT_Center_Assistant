import pandas as pd
import os
import uuid
from typing import List, Dict, Any
from app.db.client import chroma_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DataIngester:
    def __init__(self):
        self.data_directory = "data"
        self.supported_files = [
            "experience_host.csv",
            "guest.csv", 
            "home_host.csv",
            "service_host.csv",
            "travel_admin.csv"
        ]
    
    def load_csv_file(self, filename: str) -> pd.DataFrame:
        """Load a CSV file and return DataFrame"""
        try:
            filepath = os.path.join(self.data_directory, filename)
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return pd.DataFrame()
            
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} rows from {filename}")
            return df
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return pd.DataFrame()
    
    def process_dataframe(self, df: pd.DataFrame, source: str) -> List[Dict[str, Any]]:
        """Process DataFrame and create documents for embedding"""
        documents = []
        
        for idx, row in df.iterrows():
            # Create document text by combining all non-null values
            text_parts = []
            metadata = {"source": source, "row_id": idx}
            
            for column, value in row.items():
                if pd.notna(value) and str(value).strip():
                    text_parts.append(f"{column}: {value}")
                    metadata[column] = str(value)
            
            if text_parts:
                document_text = " | ".join(text_parts)
                documents.append({
                    "id": str(uuid.uuid4()),
                    "text": document_text,
                    "metadata": metadata
                })
        
        return documents
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into chunks for better embedding"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def ingest_csv_file(self, filename: str) -> bool:
        """Ingest a single CSV file into ChromaDB"""
        try:
            df = self.load_csv_file(filename)
            if df.empty:
                return False
            
            documents = self.process_dataframe(df, filename)
            if not documents:
                logger.warning(f"No documents created from {filename}")
                return False
            
            # Prepare data for ChromaDB
            doc_texts = []
            metadatas = []
            ids = []
            
            for doc in documents:
                # Chunk large documents
                chunks = self.chunk_text(doc["text"])
                
                for i, chunk in enumerate(chunks):
                    doc_texts.append(chunk)
                    chunk_metadata = doc["metadata"].copy()
                    chunk_metadata["chunk_id"] = i
                    metadatas.append(chunk_metadata)
                    ids.append(f"{doc['id']}_chunk_{i}")
            
            # Add to ChromaDB
            success = chroma_client.add_documents(
                documents=doc_texts,
                metadatas=metadatas,
                ids=ids
            )
            
            if success:
                logger.info(f"Successfully ingested {len(doc_texts)} chunks from {filename}")
                return True
            else:
                logger.error(f"Failed to ingest {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error ingesting {filename}: {e}")
            return False
    
    def ingest_all_files(self) -> Dict[str, bool]:
        """Ingest all supported CSV files"""
        results = {}
        
        for filename in self.supported_files:
            logger.info(f"Ingesting {filename}...")
            results[filename] = self.ingest_csv_file(filename)
        
        return results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the current collection"""
        try:
            collection = chroma_client.get_collection()
            count = collection.count()
            
            return {
                "document_count": count,
                "collection_name": settings.chroma_collection_name,
                "status": "healthy" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

# Global ingester instance
data_ingester = DataIngester()