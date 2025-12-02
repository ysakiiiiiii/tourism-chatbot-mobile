# Complete User Input to Result Flow

## Step-by-Step Process

```
USER ENTERS QUERY
     ↓
[1] API Endpoint: POST /api/chat (chatbot.py)
     ↓
[2] Input Validation & Casualness Check
     ├─ Is it casual? (hi, bye, thanks, how are you?)
     │  └─ YES → Return casual response & save to DB → END
     │
     └─ NO → Continue to context-aware search
          ↓
[3] Retrieve/Create Conversation Context (prolog_service.py)
     └─ Gets session_id from request
        └─ Loads ConversationContext for this session
           (tracks history, previously shown items, preferences)
          ↓
[4] NLP Processing (nlp_processor.py)
     ├─ Tokenization: Break query into words
     ├─ Remove stop words (common words like "the", "a", "is")
     ├─ Stemming: "running" → "run", "beaches" → "beach"
     ├─ Location Detection: Extract location if mentioned
     │  (e.g., "things in Vigan" → detected_location = "vigan")
     └─ Returns: (keywords, detected_location)
          ↓
[5] Context Enhancement (prolog_service.py)
     └─ Is this a follow-up query?
        └─ YES → Merge current keywords with previous context keywords
        └─ NO → Use current keywords as-is
          ↓
[6] Prolog Query Execution (prolog_service.py)
     ├─ Execute Prolog queries: find_by_keyword(), find_by_name(), etc.
     ├─ Match keywords against Prolog facts (stored in kb.pl)
     └─ Returns: List of matching item IDs
          ↓
[7] Fallback Search (if no Prolog results)
     └─ Direct Excel search using NLP stemming
        └─ Search across: name, location, description_keywords, full_description
          ↓
[8] Retrieve Full Item Details (prolog_service.py)
     ├─ For each matched ID:
     │  └─ Query Excel database (data_loader.py)
     │     └─ Get: name, location, description, photo, etc.
     ├─ Build photo URLs (assets/photo.jpg)
     └─ Returns: List of item dictionaries with full details
          ↓
[9] Ranking & Filtering (nlp_processor.py)
     ├─ Calculate relevance score for each item
     │  ├─ Keyword matches in name (score: 10 if exact, 5 if partial)
     │  ├─ Keyword matches in location (score: 3)
     │  ├─ Keyword matches in description (score: 2-3)
     │  ├─ Keyword matches in full description (score: 1)
     │  └─ Multi-keyword bonus (score: +5 per extra keyword)
     ├─ Apply location filter if detected
     └─ Return top N ranked results (default: 1)
          ↓
[10] Add Routing Information (utils/add_routing_info.py)
     └─ Calculate distance/routes from items to tourist spots
          ↓
[11] Generate Response (chatbot.py)
     ├─ Based on:
     │  ├─ Number of results (no results, 1 result, multiple results)
     │  └─ Whether it's a follow-up query
     └─ Generate diverse, natural response with item recommendations
          ↓
[12] Update Conversation Context (prolog_service.py)
     ├─ Add this turn to conversation history
     ├─ Track mentioned items
     ├─ Update user preferences
     └─ Update topic tracking
          ↓
[13] Save to Database (database.py)
     ├─ Create ChatHistory record:
     │  ├─ session_id
     │  ├─ user_message
     │  ├─ bot_response
     │  ├─ matched_items (JSON array of IDs)
     │  └─ timestamp
     └─ Commit to database
          ↓
[14] Return Response to Frontend (ChatResponse)
     ├─ response: Generated bot message
     ├─ matched_items: Full item details (with photos)
     ├─ session_id: For tracking conversation
     └─ timestamp: When response was generated
```

## Files Involved in Order

### 1. **Entry Point**
   - `app/main.py` - FastAPI app initialization
   - `app/routes/chatbot.py` - POST /api/chat endpoint

### 2. **Input Processing**
   - `app/services/nlp_processor.py` - Tokenize, stem, detect location
   - `app/services/conversation_context.py` - Track session state

### 3. **Core Search Logic**
   - `app/services/prolog_service.py` - Orchestrates entire search
   - `app/services/prolog_service.py` → calls Prolog KB (kb.pl)

### 4. **Data Retrieval**
   - `app/services/data_loader.py` - Loads Excel data
   - `/data/ilocos_chatbot_dataset.xlsx` - Source data
   - `app/services/excel_to_prolog.py` - Excel → Prolog conversion

### 5. **Ranking & Filtering**
   - `app/services/nlp_processor.py` - Ranks results by relevance

### 6. **Response Generation**
   - `app/routes/chatbot.py` - Generate diverse responses
   - `app/utils/add_routing_info.py` - Add route/distance info

### 7. **Persistence**
   - `app/database.py` - Save chat history
   - `app/models/schemas.py` - Data validation

---

## Data Flow Diagram

```
📱 FRONTEND (Mobile App)
  ↓ (POST request with user_message, session_id)
  
🔧 FASTAPI SERVER (app/main.py)
  ↓
  
🎯 CHATBOT ROUTE (app/routes/chatbot.py)
  ├─→ Is casual? 
  │    └─→ Return casual response
  │
  └─→ Search Flow:
       ↓
       📊 NLP PROCESSOR (app/services/nlp_processor.py)
       ├─ Tokenize: "best beaches in laoag" → ["best", "beaches", "laoag"]
       ├─ Remove stop words → ["beaches", "laoag"]
       ├─ Stem: ["beach", "laoag"]
       ├─ Detect location: "laoag"
       └─ Return: (["beach"], "laoag")
       ↓
       📚 PROLOG SERVICE (app/services/prolog_service.py)
       ├─ Get context: Check previous queries
       ├─ Execute Prolog queries
       │  └─→ PROLOG KB (app/prolog/kb.pl)
       │      ├─ item(ts01, 'Bangui Windmills', tourist_spot, 'bangui')
       │      ├─ has_keyword(ts01, 'beach')
       │      └─ description(ts01, '...')
       ├─ Get Excel data
       │  └─→ DATA LOADER (app/services/data_loader.py)
       │      └─→ EXCEL FILE (/data/ilocos_chatbot_dataset.xlsx)
       │         ├─ Column: name
       │         ├─ Column: location
       │         ├─ Column: description_keywords
       │         ├─ Column: full_description
       │         └─ Column: photo
       └─ Return matched items
       ↓
       🏆 NLP RANKER (app/services/nlp_processor.py)
       ├─ Score each item by relevance
       ├─ Filter by location
       └─ Return top N results
       ↓
       📍 ROUTING (app/utils/add_routing_info.py)
       └─ Add distance/route info
       ↓
       💬 RESPONSE GENERATOR (app/routes/chatbot.py)
       ├─ Generate natural response
       ├─ Format matched items
       └─ Include photos, descriptions
       ↓
       💾 DATABASE (app/database.py)
       └─ Save ChatHistory record
       ↓
       ✅ RETURN RESPONSE
          ├─ response: "Great! Here's a beautiful beach..."
          ├─ matched_items: [{name, photo_url, description, ...}]
          ├─ session_id: "abc123"
          └─ timestamp: "2025-12-02T10:30:00"
          
          ↓
📱 FRONTEND displays results to user
```

---

## Example: User Query "What are the best beaches?"

### Input:
```json
{
  "message": "What are the best beaches?",
  "session_id": "user123_session456"
}
```

### Processing:

1. **NLP**: Extracts keywords ["beach"], location = None
2. **Prolog**: Queries for items with "beach" keyword
3. **Excel**: Retrieves details (name, description, photo, etc.)
4. **Ranking**: Sorts by relevance score
5. **Response**: "Here are some beautiful beaches in Ilocos! 🏖️"

### Output:
```json
{
  "response": "Here are some beautiful beaches in Ilocos! 🏖️",
  "matched_items": [
    {
      "id": "ts02",
      "name": "Bangui Windmills",
      "location": "Bangui, Ilocos Norte",
      "description_keywords": "beach, scenic, sunset, viewpoint",
      "full_description": "A scenic beach known for...",
      "photo_url": "assets/bangui.jpg"
    }
  ],
  "session_id": "user123_session456",
  "timestamp": "2025-12-02T10:30:00"
}
```

---

## Key Technologies & Patterns

- **Prolog**: Rule-based knowledge base for intelligent queries
- **NLP**: Custom stemming & tokenization (no external ML libraries)
- **Singleton Pattern**: NLP processor, Prolog service reused across requests
- **Session Management**: Track per-user conversation context
- **Fallback Search**: Direct Excel search if Prolog returns nothing
- **Ranking Algorithm**: Weighted scoring based on match location and type
