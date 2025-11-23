from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class TransportMode(str, Enum):
    WALKING = "walking"
    JEEPNEY = "jeepney"
    TRICYCLE = "tricycle"
    BUS = "bus"
    VAN = "van"

class LocationRequest(BaseModel):
    latitude: float = Field(..., description="User's current latitude")
    longitude: float = Field(..., description="User's current longitude")
    destination_id: str = Field(..., description="Destination item ID (e.g., CU01, TS01)")
    
class RouteStep(BaseModel):
    step_number: int
    instruction: str
    transport_mode: TransportMode
    from_location: str
    to_location: str
    distance_km: float
    fare: Optional[float] = None
    estimated_time_minutes: int
    landmark: Optional[str] = None
    
class RouteResponse(BaseModel):
    destination_name: str
    destination_location: str
    total_distance_km: float
    total_fare: float
    total_time_minutes: int
    steps: List[RouteStep]
    warnings: List[str] = []
    
class NearbyPlace(BaseModel):
    id: str
    name: str
    type: str
    location: str
    distance_km: float
    walking_distance: bool  # < 1km
    estimated_walking_time: Optional[int] = None  # minutes