from pydantic import BaseModel
from typing import Optional

class Cuisine(BaseModel):
    id: str
    name: str
    type: str
    location: str
    description_keywords: str
    full_description: str
    best_time_to_visit: str
    related_items: Optional[str] = None
    nearest_hub: str

class CuisineCreate(BaseModel):
    name: str
    type: str
    location: str
    description_keywords: str
    full_description: str
    best_time_to_visit: str
    related_items: Optional[str] = None
    nearest_hub: str

class CuisineUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    description_keywords: Optional[str] = None
    full_description: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    related_items: Optional[str] = None
    nearest_hub: Optional[str] = None