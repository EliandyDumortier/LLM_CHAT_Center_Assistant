from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any
from app.rag.ingest import data_ingester
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

class IngestResponse(BaseModel):
    message: str
    results: Dict[str, Any]
    status: str

@router.post("/ingest_csv", response_model=IngestResponse)
async def ingest_csv_files(background_tasks: BackgroundTasks):
    """
    Ingest all CSV files from the data directory into ChromaDB.
    This endpoint processes all supported CSV files and creates embeddings.
    """
    try:
        logger.info("Starting CSV ingestion process")
        
        # Run ingestion in background to avoid timeout
        def run_ingestion():
            return data_ingester.ingest_all_files()
        
        # For now, run synchronously. In production, consider using background tasks
        results = run_ingestion()
        
        # Check if any files were successfully ingested
        successful_files = [f for f, success in results.items() if success]
        failed_files = [f for f, success in results.items() if not success]
        
        if successful_files:
            message = f"Successfully ingested {len(successful_files)} files"
            status = "success"
        else:
            message = "No files were successfully ingested"
            status = "error"
        
        if failed_files:
            message += f". Failed to ingest: {', '.join(failed_files)}"
        
        return IngestResponse(
            message=message,
            results=results,
            status=status
        )
        
    except Exception as e:
        logger.error(f"Error during CSV ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest CSV files: {str(e)}"
        )

@router.get("/collection_stats")
async def get_collection_stats():
    """
    Get statistics about the current ChromaDB collection.
    """
    try:
        stats = data_ingester.get_collection_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collection stats: {str(e)}"
        )

@router.post("/reset_collection")
async def reset_collection():
    """
    Reset the ChromaDB collection (USE WITH CAUTION).
    This will delete all existing data.
    """
    try:
        from app.db.client import chroma_client
        
        success = chroma_client.reset_collection()
        
        if success:
            return {
                "status": "success",
                "message": "Collection reset successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to reset collection"
            )
            
    except Exception as e:
        logger.error(f"Error resetting collection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset collection: {str(e)}"
        )