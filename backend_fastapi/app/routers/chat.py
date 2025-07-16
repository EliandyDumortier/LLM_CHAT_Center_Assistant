from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.rag.query import rag_query_engine
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory storage for chat sessions (use Redis in production)
chat_sessions = {}
pending_chats = []

class ChatMessage(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    user_id: str
    sources: List[Dict[str, Any]]
    timestamp: datetime
    status: str

class AgentResponse(BaseModel):
    session_id: str
    agent_response: str

@router.post("/query", response_model=ChatResponse)
async def process_chat_query(chat_message: ChatMessage):
    """
    Process a user chat message through the RAG pipeline.
    This endpoint handles customer queries and returns AI-generated responses.
    """
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Process the query through RAG
        result = rag_query_engine.query(
            question=chat_message.message,
            user_id=chat_message.user_id
        )
        
        # Create chat response
        response = ChatResponse(
            response=result["response"],
            session_id=session_id,
            user_id=chat_message.user_id,
            sources=result.get("sources", []),
            timestamp=datetime.now(),
            status=result.get("status", "success")
        )
        
        # Store in session (for agent console)
        chat_sessions[session_id] = {
            "user_id": chat_message.user_id,
            "messages": chat_sessions.get(session_id, {}).get("messages", []),
            "last_activity": datetime.now()
        }
        
        chat_sessions[session_id]["messages"].append({
            "type": "user",
            "content": chat_message.message,
            "timestamp": datetime.now()
        })
        
        chat_sessions[session_id]["messages"].append({
            "type": "assistant",
            "content": result["response"],
            "timestamp": datetime.now(),
            "sources": result.get("sources", [])
        })
        
        # Add to pending chats for agent console
        pending_chats.append({
            "session_id": session_id,
            "user_id": chat_message.user_id,
            "latest_message": chat_message.message,
            "ai_response": result["response"],
            "timestamp": datetime.now(),
            "status": "pending_review"
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat query: {str(e)}"
        )

@router.get("/pending")
async def get_pending_chats():
    """
    Get pending chats for the agent console.
    Returns chats that need agent review or response.
    """
    try:
        return {
            "status": "success",
            "pending_chats": pending_chats[-10:],  # Return last 10 pending chats
            "total_pending": len(pending_chats)
        }
    except Exception as e:
        logger.error(f"Error getting pending chats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending chats: {str(e)}"
        )

@router.post("/agent_respond")
async def agent_respond(agent_response: AgentResponse):
    """
    Allow agent to send a response to a chat session.
    """
    try:
        session_id = agent_response.session_id
        
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )
        
        # Add agent response to session
        chat_sessions[session_id]["messages"].append({
            "type": "agent",
            "content": agent_response.agent_response,
            "timestamp": datetime.now()
        })
        
        # Remove from pending chats
        global pending_chats
        pending_chats = [chat for chat in pending_chats if chat["session_id"] != session_id]
        
        return {
            "status": "success",
            "message": "Agent response sent successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error sending agent response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send agent response: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_chat_session(session_id: str):
    """
    Get a specific chat session history.
    """
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )
        
        return {
            "status": "success",
            "session": chat_sessions[session_id]
        }
        
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get chat session: {str(e)}"
        )

@router.get("/health")
async def chat_health_check():
    """
    Health check endpoint for chat functionality.
    """
    try:
        rag_health = rag_query_engine.health_check()
        return {
            "status": "healthy",
            "rag_engine": rag_health,
            "active_sessions": len(chat_sessions),
            "pending_chats": len(pending_chats)
        }
    except Exception as e:
        logger.error(f"Error in chat health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }