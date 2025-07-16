from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import ingest, chat
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Call Center Assistant",
    description="RAG-powered customer service assistant with Ollama and ChromaDB",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Call Center Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check database connection
        from app.db.client import chroma_client
        collection_stats = chroma_client.get_collection().count()
        
        # Check RAG engine
        from app.rag.query import rag_query_engine
        rag_health = rag_query_engine.health_check()
        
        return {
            "status": "healthy",
            "database": {
                "status": "connected",
                "document_count": collection_stats
            },
            "rag_engine": rag_health,
            "api_config": {
                "ollama_url": settings.ollama_url,
                "ollama_model": settings.ollama_model,
                "debug": settings.debug
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )