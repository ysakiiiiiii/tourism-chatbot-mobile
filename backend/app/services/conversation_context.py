"""
Conversation Context Manager
Maintains conversation history and context for follow-up queries
"""
from datetime import datetime, timedelta
from collections import deque
from typing import List, Dict, Optional, Set, Union

class ConversationContext:
    """
    Manages conversation context for a single session
    Tracks: user queries, bot responses, mentioned items, topics, and preferences
    """
    
    def __init__(self, session_id: str, max_history: int = 10):
        self.session_id = session_id
        self.max_history = max_history
        
        # Conversation history
        self.history = deque(maxlen=max_history)  # List of {query, response, timestamp, items}
        
        # Context tracking
        self.last_query = None
        self.last_keywords = []
        self.last_items = []  # Items shown in last response
        self.mentioned_items = set()  # All items mentioned in conversation
        
        # User preferences extracted from conversation
        self.preferences = {
            'locations': set(),  # Preferred locations
            'types': set(),      # Preferred types (beach, food, cave, etc)
            'keywords': set(),   # Recurring keywords (adventure, nature, peaceful, etc)
        }
        
        # Contextual state
        self.current_topic = None  # Current conversation topic
        self.expecting_followup = False  # Is next query likely a follow-up?
        
        # Session metadata
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.turn_count = 0
    
    def add_turn(self, query: str, keywords: Union[List[str], tuple], response: str, items: List[Dict]):
        """Add a conversation turn to history"""
        self.turn_count += 1
        self.last_activity = datetime.now()
        
        # Ensure keywords is a list
        if isinstance(keywords, tuple):
            # If keywords is a tuple (keywords, location), extract just keywords
            if len(keywords) == 2 and isinstance(keywords[0], list):
                keywords = keywords[0]
            else:
                keywords = list(keywords)
        elif not isinstance(keywords, list):
            keywords = [keywords]
        
        # Store in history
        turn = {
            'query': query,
            'keywords': keywords,
            'response': response,
            'items': items,
            'timestamp': datetime.now()
        }
        self.history.append(turn)
        
        # Update context
        self.last_query = query
        self.last_keywords = keywords
        self.last_items = items
        
        # Track mentioned items
        for item in items:
            if 'id' in item:
                self.mentioned_items.add(item['id'])
        
        # Extract preferences from successful queries
        if items:
            self._extract_preferences(keywords, items)
        
        # Set topic based on items
        if items:
            self.current_topic = items[0].get('type', None)
            self.expecting_followup = True
        else:
            self.expecting_followup = False
    
    def _extract_preferences(self, keywords: List[str], items: List[Dict]):
        """Extract user preferences from successful queries"""
        # Track preferences from items
        for item in items:
            # Track preferred locations
            if 'location' in item and item['location']:
                location = str(item['location']).lower().strip()
                if location and location != 'n/a':
                    self.preferences['locations'].add(location)
            
            # Track preferred types
            if 'type' in item and item['type']:
                item_type = str(item['type']).lower().strip()
                if item_type and item_type != 'n/a':
                    self.preferences['types'].add(item_type)
        
        # Track recurring keywords (ensure they're strings)
        for keyword in keywords:
            if keyword is not None:
                # Handle if keyword is a list (shouldn't happen, but defensive)
                if isinstance(keyword, (list, tuple)):
                    for kw in keyword:
                        if kw and isinstance(kw, str):
                            self.preferences['keywords'].add(kw.lower().strip())
                elif isinstance(keyword, str):
                    keyword_clean = keyword.lower().strip()
                    if keyword_clean:
                        self.preferences['keywords'].add(keyword_clean)
    
    def get_context_keywords(self) -> Set[str]:
        """
        Get relevant context keywords from conversation history
        Used to enhance current query with context
        """
        context_keywords = set()
        
        # Add keywords from last 2-3 turns
        recent_turns = list(self.history)[-3:]
        for turn in recent_turns:
            turn_keywords = turn.get('keywords', [])
            if turn_keywords:
                # Ensure keywords are strings
                for kw in turn_keywords:
                    if isinstance(kw, str):
                        context_keywords.add(kw)
        
        return context_keywords
    
    def is_followup_query(self, query: str) -> bool:
        """
        Detect if current query is a follow-up to previous conversation
        
        Follow-up indicators:
        - Starts with: "another", "different", "more", "other", "alternative"
        - Contains: "instead", "else", "besides", "similar"
        - Pronouns: "it", "that", "this", "there"
        - Short queries without specific keywords
        """
        query_lower = query.lower().strip()
        
        # Check for follow-up indicators
        followup_starters = ['another', 'different', 'more', 'other', 'alternative', 
                            'also', 'else', 'besides']
        followup_contains = ['instead', 'similar', 'like that', 'like this']
        pronouns = ['it', 'that', 'this', 'there']
        
        # Starts with follow-up word
        if any(query_lower.startswith(word) for word in followup_starters):
            return True
        
        # Contains follow-up phrase
        if any(phrase in query_lower for phrase in followup_contains):
            return True
        
        # Short query with pronoun (likely referring to previous context)
        words = query_lower.split()
        if len(words) <= 5 and any(pronoun in words for pronoun in pronouns):
            return True
        
        # Very short query after showing results (likely wants alternatives)
        if len(words) <= 3 and self.last_items:
            return True
        
        return False
    
    def should_reset(self) -> bool:
        """
        Determine if conversation context should be reset
        
        Reset conditions:
        - Session inactive for > 30 minutes
        - User explicitly asks for new search
        - Topic completely changes
        """
        # Check inactivity
        inactive_duration = datetime.now() - self.last_activity
        if inactive_duration > timedelta(minutes=30):
            return True
        
        return False
    
    def reset(self):
        """Reset conversation context (start fresh)"""
        self.history.clear()
        self.last_query = None
        self.last_keywords = []
        self.last_items = []
        self.mentioned_items.clear()
        self.preferences = {
            'locations': set(),
            'types': set(),
            'keywords': set(),
        }
        self.current_topic = None
        self.expecting_followup = False
        self.turn_count = 0
        self.last_activity = datetime.now()
    
    def get_summary(self) -> Dict:
        """Get conversation summary for debugging"""
        return {
            'session_id': self.session_id,
            'turn_count': self.turn_count,
            'current_topic': self.current_topic,
            'last_items': [item.get('name', 'Unknown') for item in self.last_items],
            'preferences': {
                'locations': list(self.preferences['locations']),
                'types': list(self.preferences['types']),
                'keywords': list(self.preferences['keywords'])
            },
            'expecting_followup': self.expecting_followup
        }


class ConversationManager:
    """
    Manages multiple conversation contexts (sessions)
    Handles session creation, retrieval, and cleanup
    """
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, ConversationContext] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def get_or_create_session(self, session_id: str) -> ConversationContext:
        """Get existing session or create new one"""
        # Check if session exists
        if session_id in self.sessions:
            context = self.sessions[session_id]
            
            # Check if session should be reset due to inactivity
            if context.should_reset():
                print(f"Session {session_id} timed out, resetting...")
                context.reset()
            
            return context
        
        # Create new session
        print(f"Creating new session: {session_id}")
        context = ConversationContext(session_id)
        self.sessions[session_id] = context
        return context
    
    def reset_session(self, session_id: str):
        """Explicitly reset a session"""
        if session_id in self.sessions:
            self.sessions[session_id].reset()
            print(f"Session {session_id} reset")
    
    def delete_session(self, session_id: str):
        """Delete a session completely"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"Session {session_id} deleted")
    
    def cleanup_old_sessions(self):
        """Remove inactive sessions"""
        now = datetime.now()
        to_delete = []
        
        for session_id, context in self.sessions.items():
            if now - context.last_activity > self.session_timeout:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            del self.sessions[session_id]
            print(f"Cleaned up session: {session_id}")
        
        return len(to_delete)
    
    def get_active_sessions_count(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)


# Singleton instance
_conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get or create conversation manager singleton"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager