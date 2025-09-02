"""
OpenAI Assistant Chat API endpoints for the landing page chat widget
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import openai
from openai import OpenAI
import logging
import json
import time
from datetime import datetime

from core.config import get_settings
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)

# Assistant ID from OpenAI Dashboard
ASSISTANT_ID = "asst_sfmtJkTcdBh6Y80zQ50fF92g"

# In-memory thread storage (in production, use Redis or database)
# This maps session_id to thread_id
thread_storage: Dict[str, str] = {}

class ChatMessage(BaseModel):
    message: str
    session_id: str
    
class ChatResponse(BaseModel):
    message: str
    thread_id: str
    session_id: str

class ThreadInfo(BaseModel):
    thread_id: str
    session_id: str
    created_at: str

@router.post("/chat/assistant/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """
    Send a message to the OpenAI Assistant and get a response
    """
    try:
        # Get or create thread for this session
        thread_id = thread_storage.get(chat_message.session_id)
        
        if not thread_id:
            # Create a new thread
            thread = client.beta.threads.create()
            thread_id = thread.id
            thread_storage[chat_message.session_id] = thread_id
            logger.info(f"Created new thread {thread_id} for session {chat_message.session_id}")
        
        # Add the user message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=chat_message.message
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # Wait for the run to complete (with timeout)
        max_attempts = 30  # 30 seconds timeout
        attempts = 0
        
        while attempts < max_attempts:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                logger.error(f"Run failed with status: {run_status.status}")
                raise HTTPException(status_code=500, detail=f"Assistant run failed: {run_status.status}")
            
            time.sleep(1)
            attempts += 1
        
        if attempts >= max_attempts:
            raise HTTPException(status_code=504, detail="Assistant response timeout")
        
        # Get the messages
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        
        # Get the latest assistant message
        assistant_message = None
        for msg in messages.data:
            if msg.role == "assistant":
                # Extract text from the message content
                if msg.content and len(msg.content) > 0:
                    content = msg.content[0]
                    if hasattr(content, 'text'):
                        assistant_message = content.text.value
                        break
        
        if not assistant_message:
            assistant_message = "I apologize, but I couldn't generate a response. Please try again."
        
        return ChatResponse(
            message=assistant_message,
            thread_id=thread_id,
            session_id=chat_message.session_id
        )
        
    except openai.AuthenticationError:
        logger.error("OpenAI API authentication failed")
        raise HTTPException(status_code=500, detail="Chat service authentication error")
    except openai.RateLimitError:
        logger.error("OpenAI API rate limit exceeded")
        raise HTTPException(status_code=429, detail="Chat service is temporarily unavailable. Please try again later.")
    except Exception as e:
        logger.error(f"Error in assistant chat: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your message")

@router.get("/chat/assistant/thread/{session_id}", response_model=ThreadInfo)
async def get_thread_info(session_id: str):
    """
    Get thread information for a session
    """
    thread_id = thread_storage.get(session_id)
    
    if not thread_id:
        raise HTTPException(status_code=404, detail="No thread found for this session")
    
    return ThreadInfo(
        thread_id=thread_id,
        session_id=session_id,
        created_at=datetime.utcnow().isoformat()
    )

@router.delete("/chat/assistant/thread/{session_id}")
async def clear_thread(session_id: str):
    """
    Clear the thread for a session (start a new conversation)
    """
    if session_id in thread_storage:
        thread_id = thread_storage.pop(session_id)
        logger.info(f"Cleared thread {thread_id} for session {session_id}")
        return {"message": "Thread cleared successfully", "session_id": session_id}
    
    return {"message": "No thread to clear", "session_id": session_id}

@router.get("/chat/assistant/health")
async def health_check():
    """
    Check if the assistant chat service is healthy
    """
    try:
        # Try to retrieve the assistant to verify connection
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
        return {
            "status": "healthy",
            "assistant_id": ASSISTANT_ID,
            "assistant_name": assistant.name,
            "service": "OpenAI Assistant Chat"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "OpenAI Assistant Chat"
        }