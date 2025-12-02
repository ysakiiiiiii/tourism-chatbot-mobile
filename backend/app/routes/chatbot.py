"""
Enhanced context-aware chatbot endpoint with casual conversation support
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.prolog_service import get_prolog_service
from app.services.nlp_processor import get_nlp_processor
from app.services.conversation_context import get_conversation_manager
from app.utils.add_routing_info import add_routing_info
from app.database import get_db, ChatHistory
from datetime import datetime
import json
import uuid
import random

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

# Casual conversation patterns
GREETINGS = {
    'hi', 'hello', 'hey', 'hii', 'hiii', 'hiiii', 'good morning', 
    'good afternoon', 'good evening', 'greetings', 'yo', 'sup', 'wassup',
    'helloo', 'hellooo'
}

GREETING_RESPONSES = [
    "Hello! 👋 I'm your Ilocos tour guide. What kind of places would you like to explore?",
    "Hi there! 😊 I can help you discover amazing spots in Ilocos. What are you interested in?",
    "Hey! Ready to explore Ilocos? Tell me what you're looking for - beaches, food, heritage sites?",
    "Good day! 🌟 I'm here to help you find the best places in Ilocos. What catches your interest?",
    "Hi! 🗺️ Welcome to your Ilocos adventure! What would you like to discover today?",
]

THANKS = {
    'thanks', 'thank you', 'thank you so much', 'ty', 'tysm', 'thx', 'thnx',
    'thank u', 'thankyou', 'thanks a lot', 'appreciate it'
}

THANKS_RESPONSES = [
    "You're welcome! 😊 Anything else you'd like to know?",
    "Happy to help! Feel free to ask if you need more recommendations.",
    "My pleasure! Let me know if you want to explore more places.",
    "Glad I could assist! What else would you like to discover?",
    "Anytime! Ready to help you find more amazing spots. 🌟",
]

HOW_ARE_YOU = {
    'how are you', 'how r u', 'hows it going', 'whats up', "what's up", 
    'how have you been', 'how do you do', 'hru', 'how are u'
}

HOW_ARE_YOU_RESPONSES = [
    "I'm doing great, thanks for asking! 😊 Ready to help you explore Ilocos. What are you interested in?",
    "I'm excellent! Excited to share amazing places with you. What would you like to find?",
    "Doing wonderful! I love helping people discover Ilocos. What kind of experience are you looking for?",
    "I'm fantastic! 🌟 Let's find some awesome places for you. What catches your eye?",
]

GOODBYES = {
    'bye', 'goodbye', 'see you', 'see ya', 'later', 'gtg', 'gotta go',
    'talk to you later', 'ttyl', 'catch you later', 'bye bye', 'byeee'
}

GOODBYE_RESPONSES = [
    "Goodbye! 👋 Come back anytime you want to explore more of Ilocos. Safe travels!",
    "See you later! 🌟 Hope you enjoy your Ilocos adventure!",
    "Take care! Come back if you need more recommendations. Happy exploring! 🗺️",
    "Bye! 😊 Have an amazing time in Ilocos!",
]


def is_casual_conversation(message: str) -> tuple[bool, str]:
    """
    Detect casual conversation and return appropriate response
    Returns: (is_casual, response_text)
    """
    msg_lower = message.lower().strip()
    
    # Remove punctuation for matching
    msg_clean = msg_lower.rstrip('!?.,')
    
    # Check for greetings
    if msg_clean in GREETINGS or any(greet in msg_clean.split() for greet in GREETINGS):
        return True, random.choice(GREETING_RESPONSES)
    
    # Check for thanks
    if msg_clean in THANKS or any(thank in msg_lower for thank in THANKS):
        return True, random.choice(THANKS_RESPONSES)
    
    # Check for "how are you" type questions
    if any(phrase in msg_lower for phrase in HOW_ARE_YOU):
        return True, random.choice(HOW_ARE_YOU_RESPONSES)
    
    # Check for goodbye
    if msg_clean in GOODBYES or any(bye in msg_clean.split() for bye in GOODBYES):
        return True, random.choice(GOODBYE_RESPONSES)
    
    return False, ""


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    top_n: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """
    Enhanced chat endpoint with context awareness and casual conversation
    
    Features:
    - Handles casual greetings and small talk
    - Maintains conversation context per session
    - Detects follow-up queries
    - Filters previously shown items
    - Diverse, natural responses
    
    Args:
        request: Chat request with message and optional session_id
        top_n: Number of results (default: 3, max: 10)
    """
    try:
        user_message = request.message.strip()
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Empty message")
        
        # Validate top_n
        top_n = max(1, min(top_n, 10))
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Check for casual conversation first
        is_casual, casual_response = is_casual_conversation(user_message)
        if is_casual:
            # Save casual conversation to history
            chat_record = ChatHistory(
                session_id=session_id,
                user_message=user_message,
                bot_response=casual_response,
                matched_items=json.dumps([]),
                timestamp=datetime.utcnow()
            )
            db.add(chat_record)
            await db.commit()
            
            return ChatResponse(
                response=casual_response,
                matched_items=[],
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
        
        # Get services
        prolog_service = get_prolog_service()
        nlp = get_nlp_processor()
        conversation_manager = get_conversation_manager()
        
        # Get or create conversation context
        context = conversation_manager.get_or_create_session(session_id)
        
        # Check for reset commands
        reset_commands = ['new search', 'start over', 'reset', 'start fresh']
        if any(cmd in user_message.lower() for cmd in reset_commands):
            prolog_service.reset_conversation(session_id)
            response_text = random.choice([
                "Sure! Let's start fresh. 🔄 What kind of place are you looking for?",
                "Okay, starting over! What would you like to explore in Ilocos?",
                "Fresh start! 🌟 Tell me what you're interested in finding.",
            ])
            matched_items = []
        else:
            # Use context-aware search from prolog service
            matched_items, context = prolog_service.search_with_context(
                user_message, 
                session_id, 
                top_n=top_n
            )
            
            matched_items = add_routing_info(matched_items)
            
            # Process query to get keywords (for response generation)
            keywords = nlp.process_query(user_message)
            
            # Detect if this is a follow-up query
            is_followup = context.is_followup_query(user_message)
            
            # Generate diverse response
            response_text = generate_response(
                matched_items, 
                is_followup, 
                user_message,
                context
            )
            
            # Update conversation context (add this turn to history)
            prolog_service.update_conversation_context(
                session_id,
                user_message,
                keywords,
                response_text,
                matched_items
            )
        
        # Save to database
        chat_record = ChatHistory(
            session_id=session_id,
            user_message=user_message,
            bot_response=response_text,
            matched_items=json.dumps([item.get('id', '') for item in matched_items]),
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
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


def generate_response(items, is_followup, user_query, context):
    """Generate diverse, natural responses based on context"""
    
    if not items:
        # No results - diverse responses
        # Special case: follow-up alternatives exhausted -> explicit message
        if is_followup and getattr(context, 'last_alternatives_exhausted', False):
            context.last_alternatives_exhausted = False
            return "I've already shown all different options I have for that. There are no more alternatives right now. Would you like to search a different area or try another type of place?"

        if is_followup:
            no_results_responses = [
                "Hmm, I couldn't find any other options matching that. 🤔 Would you like to try a different area or type of place?",
                "I've shown you all the best matches I have for that. Want to explore something different?",
                "That's all I've got for now! How about trying a different location or activity?",
                "No more matches for those criteria. 😕 Want to search for something else?",
            ]
            return random.choice(no_results_responses)
        else:
            no_results_responses = [
                "I couldn't find anything matching that. 😕 Try describing what you're looking for differently - maybe mention a location, activity, or type of place?",
                "Hmm, no matches found. Could you rephrase? For example: 'beaches in Pagudpud' or 'heritage sites in Vigan'",
                "I'm not finding results for that. Try asking about tourist spots, food places, or specific locations in Ilocos!",
                "No results for that search. 🔍 Try being more specific - mention a location or type of place you're interested in.",
            ]
            return random.choice(no_results_responses)
    
    # Has results
    if is_followup:
        # Follow-up responses
        if len(items) == 1:
            item = items[0]
            responses = [
                f"How about {item['name']} in {item['location']}? 🌟",
                f"Here's another great option: {item['name']} ({item['location']}). Would you like more details?",
                f"You might also like {item['name']} - it's in {item['location']}!",
                f"Check out {item['name']} in {item['location']}! Interested? 🗺️",
            ]
        else:
            place_list = ', '.join([f"{item['name']}" for item in items[:2]])
            more_text = f" and {len(items)-2} more" if len(items) > 2 else ""
            responses = [
                f"Here are some other great options: {place_list}{more_text}. Want to know more about any of these?",
                f"Check out these alternatives: {place_list}{more_text}. Which one interests you?",
                f"I also recommend: {place_list}{more_text}. Would you like details on these? 🌟",
                f"How about: {place_list}{more_text}. Any of these catch your eye? 👀",
            ]
        return random.choice(responses)
    
    else:
        # First query responses - more detailed
        if len(items) == 1:
            item = items[0]
            base = f"I found {item['name']} in {item['location']}! ✨"
            
            # Add extra details if available
            extras = []
            if item.get('best_time_to_visit'):
                extras.append(f"Best time: {item['best_time_to_visit']}")
            if item.get('description_keywords'):
                desc = str(item['description_keywords'])
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                extras.append(desc)
            elif item.get('full_description'):
                desc = str(item['full_description'])
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                extras.append(desc)
            
            if extras:
                base += "\n" + " • ".join(extras)
            
            base += "\n\nWant to see more options?"
            return base
        
        else:
            # Multiple results
            if len(items) == 2:
                place_list = f"{items[0]['name']} and {items[1]['name']}"
            else:
                place_list = ', '.join([item['name'] for item in items[:2]])
                if len(items) > 2:
                    place_list += f", and {len(items)-2} more"
            
            responses = [
                f"I found several great places! Including {place_list}. Which would you like to know more about? 🗺️",
                f"Here are some top picks: {place_list}. Want details on any of these? ✨",
                f"Check out these spots: {place_list}. Interested in learning more?",
                f"Great options ahead! {place_list}. Which catches your interest? 👀",
            ]
            return random.choice(responses)


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
            .order_by(ChatHistory.timestamp.asc())
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
    """Delete chat history and reset context for a session"""
    try:
        # Delete from database
        result = await db.execute(
            select(ChatHistory).where(ChatHistory.session_id == session_id)
        )
        records = result.scalars().all()
        
        for record in records:
            await db.delete(record)
        
        await db.commit()
        
        # Reset conversation context in prolog service
        prolog_service = get_prolog_service()
        prolog_service.reset_conversation(session_id)
        
        return {
            "message": f"Deleted {len(records)} records and reset context for session {session_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting history: {str(e)}")


@router.get("/context/{session_id}")
async def get_context(session_id: str):
    """Get conversation context for debugging"""
    try:
        prolog_service = get_prolog_service()
        summary = prolog_service.get_conversation_summary(session_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{session_id}")
async def reset_context(session_id: str):
    """Reset conversation context without deleting database history"""
    try:
        prolog_service = get_prolog_service()
        prolog_service.reset_conversation(session_id)
        return {"message": f"Context reset for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        prolog_service = get_prolog_service()
        conversation_manager = get_conversation_manager()
        active_sessions = conversation_manager.get_active_sessions_count()
        
        return {
            "status": "ok",
            "service": "LocaTour Chatbot",
            "active_sessions": active_sessions,
            "features": [
                "Context-aware conversations",
                "Casual chat support",
                "Follow-up detection",
                "Session persistence"
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "LocaTour Chatbot",
            "error": str(e)
        }