from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# Chatbot Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message/query")
    session_id: Optional[str] = Field(None, description="Session ID for tracking conversation")

class ChatResponse(BaseModel):
    response: str
    matched_items: List[dict]
    session_id: str
    timestamp: datetime

# Tourist Spot Schemas
class TouristSpotBase(BaseModel):
    id: str
    name: str
    type: str
    location: str
    description_keywords: Optional[str] = None
    full_description: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    related_items: Optional[str] = None
    nearest_hub: Optional[str] = None

class TouristSpotCreate(TouristSpotBase):
    pass

class TouristSpotUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    description_keywords: Optional[str] = None
    full_description: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    related_items: Optional[str] = None
    nearest_hub: Optional[str] = None

class TouristSpot(TouristSpotBase):
    class Config:
        from_attributes = True

# Cuisine Schemas
class CuisineBase(BaseModel):
    id: str
    name: str
    type: str
    location: str
    description_keywords: Optional[str] = None
    full_description: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    related_items: Optional[str] = None
    nearest_hub: Optional[str] = None

class CuisineCreate(CuisineBase):
    pass

class CuisineUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    description_keywords: Optional[str] = None
    full_description: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    related_items: Optional[str] = None
    nearest_hub: Optional[str] = None

class Cuisine(CuisineBase):
    class Config:
        from_attributes = True

# Chat History Schemas
class ChatHistoryResponse(BaseModel):
    id: int
    session_id: str
    user_message: str
    bot_response: str
    matched_items: str
    timestamp: datetime

    class Config:
        from_attributes = True