from fastapi import APIRouter, HTTPException, Query
from app.models.location_schemas import (
    LocationRequest, RouteResponse, NearbyPlace
)
from app.services.routing_service import get_routing_service
from typing import List

router = APIRouter(prefix="/api/location", tags=["Location & Routing"])

@router.post("/route", response_model=RouteResponse)
async def get_route(request: LocationRequest):
    """
    Get route from user's current location to a destination
    
    Example:
    ```json
    {
      "latitude": 18.1984,
      "longitude": 120.5936,
      "destination_id": "CU01"
    }
    ```
    
    Returns step-by-step directions with transport modes and fares
    """
    try:
        routing_service = get_routing_service()
        
        route = routing_service.calculate_route(
            from_lat=request.latitude,
            from_lon=request.longitude,
            destination_id=request.destination_id
        )
        
        if not route:
            raise HTTPException(
                status_code=404, 
                detail=f"Destination {request.destination_id} not found or no coordinates available"
            )
        
        return route
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")

@router.get("/nearby", response_model=List[NearbyPlace])
async def get_nearby_places(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    radius_km: float = Query(5.0, description="Search radius in kilometers", ge=0.1, le=50),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=50)
):
    """
    Find places near the user's location
    
    Example:
    ```
    GET /api/location/nearby?latitude=18.1984&longitude=120.5936&radius_km=5
    ```
    
    Returns list of nearby places with distances and walking information
    """
    try:
        routing_service = get_routing_service()
        
        nearby = routing_service.find_nearby_places(
            lat=latitude,
            lon=longitude,
            radius_km=radius_km,
            limit=limit
        )
        
        return nearby
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nearby search error: {str(e)}")

@router.get("/coordinates/{location_name}")
async def get_location_coordinates(location_name: str):
    """
    Get coordinates for a specific location
    
    Example:
    ```
    GET /api/location/coordinates/Laoag
    ```
    """
    from data.location_coordinates import LOCATION_COORDINATES
    
    if location_name in LOCATION_COORDINATES:
        return {
            "location": location_name,
            "coordinates": LOCATION_COORDINATES[location_name]
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Coordinates for '{location_name}' not found"
        )

@router.get("/transport-routes")
async def get_transport_routes():
    """
    Get all available transport routes and fares
    
    Returns information about jeepney, bus, tricycle, and van routes
    """
    from data.location_coordinates import TRANSPORT_ROUTES
    
    return {
        "jeepney_routes": TRANSPORT_ROUTES['jeepney'],
        "bus_routes": TRANSPORT_ROUTES['bus'],
        "van_routes": TRANSPORT_ROUTES['van'],
        "tricycle_info": TRANSPORT_ROUTES['tricycle']
    }