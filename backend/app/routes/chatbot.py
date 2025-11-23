from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.prolog_service import get_prolog_service
from app.database import get_db, ChatHistory
from datetime import datetime
import json
import uuid

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    top_n: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat endpoint - processes natural language queries with NLP
    
    Args:
        request: Chat request with message and optional session_id
        top_n: Number of top results to return (default: 1, max: 10)
    
    Example queries:
        - "I want to see beaches in Pagudpud"
        - "find fried crispy pork"
        - "show me heritage sites"
    """
    try:
        # Validate top_n
        if top_n < 1:
            top_n = 1
        elif top_n > 10:
            top_n = 10
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get Prolog service
        prolog_service = get_prolog_service()
        
        # Search using Prolog with NLP processing
        matched_items = prolog_service.search(request.message, top_n=top_n)
        
        # Generate response
        if matched_items:
            if len(matched_items) == 1:
                response_text = f"I found the best match for your query:\n\n"
            else:
                response_text = f"I found the top {len(matched_items)} result(s) for your query:\n\n"
            
            for i, item in enumerate(matched_items, 1):
                if len(matched_items) > 1:
                    response_text += f"{i}. "
                
                response_text += f"📍 **{item['name']}** ({item['type']})\n"
                response_text += f"   Location: {item['location']}\n"
                response_text += f"   {item['full_description']}\n"
                if item.get('best_time_to_visit'):
                    response_text += f"   Best time: {item['best_time_to_visit']}\n"
                if item.get('nearest_hub'):
                    response_text += f"   Nearest hub: {item['nearest_hub']}\n"
                response_text += "\n"
        else:
            response_text = "I couldn't find any results matching your query. Try different keywords or ask about tourist spots or cuisine in Ilocos!"
        
        # Save to chat history
        chat_record = ChatHistory(
            session_id=session_id,
            user_message=request.message,
            bot_response=response_text,
            matched_items=json.dumps([item['id'] for item in matched_items]),
            timestamp=datetime.utcnow()
        )
        db.add(chat_record)
        await db.commit()
        
        return ChatResponse(
            response=response_text,
            matched_items=matched_items,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/history/{session_id}", response_model=list[ChatHistoryResponse])
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a specific session"""
    try:
        result = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.timestamp.desc())
        )
        history = result.scalars().all()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@router.get("/history", response_model=list[ChatHistoryResponse])
async def get_all_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get all chat history (limited)"""
    try:
        result = await db.execute(
            select(ChatHistory)
            .order_by(ChatHistory.timestamp.desc())
            .limit(limit)
        )
        history = result.scalars().all()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@router.delete("/history/{session_id}")
async def delete_session_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete chat history for a specific session"""
    try:
        result = await db.execute(
            select(ChatHistory).where(ChatHistory.session_id == session_id)
        )
        records = result.scalars().all()
        
        for record in records:
            await db.delete(record)
        
        await db.commit()
        return {"message": f"Deleted {len(records)} records for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting history: {str(e)}")