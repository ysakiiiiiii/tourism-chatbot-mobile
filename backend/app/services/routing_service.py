"""
Enhanced Routing and navigation service for tourists
Calculates routes, fares, and provides turn-by-turn directions
Handles both tourist_spot and cuisine types with appropriate logic
"""
import math
from typing import List, Tuple, Optional, Dict, Any
import pandas as pd
from enum import Enum
from app.config import EXCEL_FILE
from data.location_coordinates import (
    LOCATION_COORDINATES,
    TRANSPORT_ROUTES,
    WALKING_SPEED_KMH,
    WALKING_DISTANCE_THRESHOLD_KM,
    calculate_tricycle_fare,
    calculate_jeepney_fare,
    calculate_van_fare,
    calculate_bus_fare
)
from app.models.location_schemas import (
    RouteStep, RouteResponse, NearbyPlace, TransportMode
)

class ItemType(str, Enum):
    """Types of tourism items"""
    TOURIST_SPOT = "tourist_spot"
    CUISINE = "cuisine"

class RoutingService:
    def __init__(self):
        self.excel_df = pd.read_excel(EXCEL_FILE)
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_item_type(self, destination_id: str) -> Optional[str]:
        """Get the type of item (tourist_spot or cuisine)"""
        item = self.excel_df[self.excel_df['id'] == destination_id]
        if item.empty:
            return None
        return item.iloc[0].get('type', ItemType.TOURIST_SPOT)
    
    def get_destination_coordinates(self, destination_id: str) -> Optional[Tuple[float, float, str]]:
        """
        Get coordinates for a destination from the Excel database
        Returns (lat, lon, location_name) or None
        """
        item = self.excel_df[self.excel_df['id'] == destination_id]
        
        if item.empty:
            return None
        
        location_name = item.iloc[0]['location']
        
        # Try to find coordinates for this location
        if location_name in LOCATION_COORDINATES:
            coords = LOCATION_COORDINATES[location_name]
            return (coords['lat'], coords['lon'], location_name)
        
        # If exact location not found, try to find nearest hub
        nearest_hub = item.iloc[0].get('nearest_hub')
        if nearest_hub and nearest_hub in LOCATION_COORDINATES:
            coords = LOCATION_COORDINATES[nearest_hub]
            return (coords['lat'], coords['lon'], nearest_hub)
        
        return None
    
    def find_nearest_terminal(self, lat: float, lon: float) -> Tuple[str, float]:
        """
        Find the nearest terminal/hub from user's location
        Returns (terminal_name, distance_km)
        """
        min_distance = float('inf')
        nearest_terminal = None
        
        terminals = {k: v for k, v in LOCATION_COORDINATES.items() 
                    if 'Terminal' in k or k in ['Laoag', 'Batac', 'Pagudpud']}
        
        for terminal_name, coords in terminals.items():
            distance = self.haversine_distance(lat, lon, coords['lat'], coords['lon'])
            if distance < min_distance:
                min_distance = distance
                nearest_terminal = terminal_name
        
        return nearest_terminal, min_distance
    
    def _get_best_transport_mode(self, distance_km: float) -> str:
        """
        Determine the best transport mode based on distance
        - < 1km: Walking
        - 1-5km: Tricycle
        - 5-30km: Jeepney
        - 30-100km: Bus or Van
        - > 100km: Bus or Van
        """
        if distance_km <= 1:
            return "walking"
        elif distance_km <= 5:
            return "tricycle"
        elif distance_km <= 30:
            return "jeepney"
        else:
            return "bus"
    
    def calculate_route(
        self, 
        from_lat: float, 
        from_lon: float, 
        destination_id: str
    ) -> Optional[RouteResponse]:
        """
        Calculate the best route from user's location to destination
        Handles both tourist_spot and cuisine types with appropriate routing logic
        """
        # Get destination info
        dest_coords = self.get_destination_coordinates(destination_id)
        if not dest_coords:
            return None
        
        dest_lat, dest_lon, dest_location = dest_coords
        
        # Get destination item details
        dest_item = self.excel_df[self.excel_df['id'] == destination_id].iloc[0]
        dest_name = dest_item['name']
        item_type = dest_item.get('type', ItemType.TOURIST_SPOT)
        
        # Calculate total distance
        total_distance = self.haversine_distance(from_lat, from_lon, dest_lat, dest_lon)
        
        steps = []
        warnings = []
        total_fare = 0
        total_time = 0
        step_num = 1
        
        # Different routing logic based on item type
        if item_type == ItemType.CUISINE:
            # Cuisine routing: Find restaurant/food establishment location
            steps, total_fare, total_time = self._route_to_cuisine(
                from_lat, from_lon, dest_name, dest_location, total_distance,
                nearest_hub_override=dest_item.get('nearest_hub')
            )
            warnings.append("This is a food establishment. Directions lead to the restaurant location.")
        else:
            # Tourist spot routing: Traditional navigation
            steps, total_fare, total_time, route_warnings = self._route_to_tourist_spot(
                from_lat, from_lon, dest_name, dest_location, total_distance,
                nearest_terminal_info=dest_item.get('nearest_hub')
            )
            warnings.extend(route_warnings)
        
        return RouteResponse(
            destination_name=dest_name,
            destination_location=dest_location,
            total_distance_km=round(total_distance, 2),
            total_fare=round(total_fare, 2),
            total_time_minutes=total_time,
            steps=steps,
            warnings=warnings,
            item_type=item_type
        )
    
    def _route_to_tourist_spot(
        self,
        from_lat: float,
        from_lon: float,
        dest_name: str,
        dest_location: str,
        total_distance: float,
        nearest_terminal_info: Optional[str] = None
    ) -> Tuple[List[RouteStep], float, int, List[str]]:
        """
        Calculate route to a tourist spot
        """
        steps = []
        warnings = []
        total_fare = 0
        total_time = 0
        step_num = 1
        
        # If within walking distance
        if total_distance <= WALKING_DISTANCE_THRESHOLD_KM:
            walking_time = int((total_distance / WALKING_SPEED_KMH) * 60)
            steps.append(RouteStep(
                step_number=step_num,
                instruction=f"Walk directly to {dest_name}",
                transport_mode=TransportMode.WALKING,
                from_location="Your current location",
                to_location=dest_name,
                distance_km=round(total_distance, 2),
                fare=0,
                estimated_time_minutes=walking_time,
                landmark=f"Located in {dest_location}"
            ))
            total_time = walking_time
        else:
            # Find nearest terminal
            nearest_terminal, terminal_distance = self.find_nearest_terminal(from_lat, from_lon)
            
            # Step 1: Get to terminal
            if terminal_distance <= WALKING_DISTANCE_THRESHOLD_KM:
                walking_time = int((terminal_distance / WALKING_SPEED_KMH) * 60)
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Walk to {nearest_terminal}",
                    transport_mode=TransportMode.WALKING,
                    from_location="Your current location",
                    to_location=nearest_terminal,
                    distance_km=round(terminal_distance, 2),
                    fare=0,
                    estimated_time_minutes=walking_time,
                    landmark="Look for the jeepney terminal"
                ))
                total_time += walking_time
                step_num += 1
            else:
                tricycle_fare = calculate_tricycle_fare(terminal_distance)
                tricycle_time = int(terminal_distance * 5)
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take a tricycle to {nearest_terminal}",
                    transport_mode=TransportMode.TRICYCLE,
                    from_location="Your current location",
                    to_location=nearest_terminal,
                    distance_km=round(terminal_distance, 2),
                    fare=tricycle_fare,
                    estimated_time_minutes=tricycle_time,
                    landmark="Tell the driver: '{nearest_terminal}'"
                ))
                total_fare += tricycle_fare
                total_time += tricycle_time
                step_num += 1
            
            # Step 2: Main transport to destination area
            route_key = self._find_transport_route(nearest_terminal, dest_location)
            
            if route_key:
                transport_mode, route_info = route_key
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take a {transport_mode} from {nearest_terminal} to {dest_location}",
                    transport_mode=TransportMode(transport_mode),
                    from_location=nearest_terminal,
                    to_location=dest_location,
                    distance_km=round(route_info.get('distance_km', total_distance - terminal_distance), 2),
                    fare=route_info['fare'],
                    estimated_time_minutes=route_info['time_minutes'],
                    landmark=f"Look for {transport_mode}s with sign '{dest_location}'"
                ))
                total_fare += route_info['fare']
                total_time += route_info['time_minutes']
                step_num += 1
            else:
                # Estimate if no direct route
                estimated_fare = calculate_jeepney_fare(total_distance - terminal_distance)
                estimated_time = int(((total_distance - terminal_distance) / 40) * 60)
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take a jeepney towards {dest_location}",
                    transport_mode=TransportMode.JEEPNEY,
                    from_location=nearest_terminal,
                    to_location=dest_location,
                    distance_km=round(total_distance - terminal_distance, 2),
                    fare=estimated_fare,
                    estimated_time_minutes=estimated_time,
                    landmark=f"Ask driver: 'Going to {dest_location}?'"
                ))
                total_fare += estimated_fare
                total_time += estimated_time
                step_num += 1
                warnings.append("No direct route found. Fare is estimated.")
            
            # Step 3: Final destination
            steps.append(RouteStep(
                step_number=step_num,
                instruction=f"You will arrive at {dest_name}",
                transport_mode=TransportMode.WALKING,
                from_location=f"{dest_location} drop-off point",
                to_location=dest_name,
                distance_km=0,
                fare=0,
                estimated_time_minutes=0,
                landmark=f"Ask locals for '{dest_name}' - it's a well-known tourist spot!"
            ))
        
        return steps, total_fare, total_time, warnings
    
    def _route_to_cuisine(
        self,
        from_lat: float,
        from_lon: float,
        dest_name: str,
        dest_location: str,
        total_distance: float,
        nearest_hub_override: Optional[str] = None
    ) -> Tuple[List[RouteStep], float, int]:
        """
        Calculate route to a cuisine/food establishment
        Typically shorter routes, focused on dining locations
        """
        steps = []
        total_fare = 0
        total_time = 0
        step_num = 1
        
        # If within walking distance - perfect for food places
        if total_distance <= WALKING_DISTANCE_THRESHOLD_KM:
            walking_time = int((total_distance / WALKING_SPEED_KMH) * 60)
            steps.append(RouteStep(
                step_number=step_num,
                instruction=f"Walk to {dest_name}",
                transport_mode=TransportMode.WALKING,
                from_location="Your current location",
                to_location=dest_name,
                distance_km=round(total_distance, 2),
                fare=0,
                estimated_time_minutes=walking_time,
                landmark=f"Located at {dest_location}"
            ))
            total_time = walking_time
        
        # Short distance - tricycle recommended for food places
        elif total_distance <= 5:
            # Option 1: Walk (if reasonable)
            if total_distance <= 2:
                walking_time = int((total_distance / WALKING_SPEED_KMH) * 60)
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Walk to {dest_name} (or take tricycle)",
                    transport_mode=TransportMode.WALKING,
                    from_location="Your current location",
                    to_location=dest_name,
                    distance_km=round(total_distance, 2),
                    fare=0,
                    estimated_time_minutes=walking_time,
                    landmark=f"Located in {dest_location}"
                ))
                total_time = walking_time
            else:
                # Tricycle for medium distance
                tricycle_fare = calculate_tricycle_fare(total_distance)
                tricycle_time = int(total_distance * 5)
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take a tricycle to {dest_name}",
                    transport_mode=TransportMode.TRICYCLE,
                    from_location="Your current location",
                    to_location=dest_name,
                    distance_km=round(total_distance, 2),
                    fare=tricycle_fare,
                    estimated_time_minutes=tricycle_time,
                    landmark=f"Tell driver: '{dest_location}' or '{dest_name}'"
                ))
                total_fare = tricycle_fare
                total_time = tricycle_time
        
        else:
            # Longer distance - use public transport to nearby hub, then local
            nearest_hub = nearest_hub_override or self.find_nearest_terminal(from_lat, from_lon)[0]
            hub_distance = self.haversine_distance(from_lat, from_lon, 
                                                   LOCATION_COORDINATES[nearest_hub]['lat'],
                                                   LOCATION_COORDINATES[nearest_hub]['lon'])
            
            # Get to hub
            if hub_distance <= 1:
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Walk to {nearest_hub}",
                    transport_mode=TransportMode.WALKING,
                    from_location="Your current location",
                    to_location=nearest_hub,
                    distance_km=round(hub_distance, 2),
                    fare=0,
                    estimated_time_minutes=int((hub_distance / WALKING_SPEED_KMH) * 60),
                    landmark=f"Nearest hub to {dest_location}"
                ))
                total_time += int((hub_distance / WALKING_SPEED_KMH) * 60)
            else:
                tricycle_fare = calculate_tricycle_fare(hub_distance)
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take tricycle to {nearest_hub}",
                    transport_mode=TransportMode.TRICYCLE,
                    from_location="Your current location",
                    to_location=nearest_hub,
                    distance_km=round(hub_distance, 2),
                    fare=tricycle_fare,
                    estimated_time_minutes=int(hub_distance * 5),
                    landmark=f"Gateway to {dest_location}"
                ))
                total_fare += tricycle_fare
                total_time += int(hub_distance * 5)
            
            step_num += 1
            
            # From hub to food place
            remaining_distance = total_distance - hub_distance
            if remaining_distance > 0.1:
                tricycle_fare = calculate_tricycle_fare(remaining_distance)
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take tricycle to {dest_name}",
                    transport_mode=TransportMode.TRICYCLE,
                    from_location=nearest_hub,
                    to_location=dest_name,
                    distance_km=round(remaining_distance, 2),
                    fare=tricycle_fare,
                    estimated_time_minutes=int(remaining_distance * 5),
                    landmark=f"Located at {dest_location}"
                ))
                total_fare += tricycle_fare
                total_time += int(remaining_distance * 5)
        
        return steps, total_fare, total_time
    
    def _find_transport_route(self, from_loc: str, to_loc: str) -> Optional[Tuple[str, dict]]:
        """
        Find available transport route between two locations
        Returns (transport_mode, route_info) or None
        """
        from_clean = from_loc.replace(" Terminal", "").replace(" City", "")
        to_clean = to_loc.replace(" Terminal", "").replace(" City", "")
        
        route = (from_clean, to_clean)
        
        # Check in order of preference: van, bus, jeepney
        if route in TRANSPORT_ROUTES.get('van', {}):
            return ('van', TRANSPORT_ROUTES['van'][route])
        
        if route in TRANSPORT_ROUTES.get('bus', {}):
            return ('bus', TRANSPORT_ROUTES['bus'][route])
        
        if route in TRANSPORT_ROUTES.get('jeepney', {}):
            return ('jeepney', TRANSPORT_ROUTES['jeepney'][route])
        
        return None
    
    def find_nearby_places(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float = 5.0,
        limit: int = 10,
        item_type: Optional[str] = None
    ) -> List[NearbyPlace]:
        """
        Find places near the user's location
        Can filter by item_type (tourist_spot or cuisine)
        """
        nearby = []
        
        for _, item in self.excel_df.iterrows():
            # Filter by type if specified
            if item_type and item.get('type') != item_type:
                continue
            
            location = item['location']
            
            if location in LOCATION_COORDINATES:
                coords = LOCATION_COORDINATES[location]
                distance = self.haversine_distance(
                    lat, lon, 
                    coords['lat'], coords['lon']
                )
                
                if distance <= radius_km:
                    is_walking = distance <= WALKING_DISTANCE_THRESHOLD_KM
                    walking_time = None
                    if is_walking:
                        walking_time = int((distance / WALKING_SPEED_KMH) * 60)
                    
                    nearby.append(NearbyPlace(
                        id=item['id'],
                        name=item['name'],
                        type=item['type'],
                        location=location,
                        distance_km=round(distance, 2),
                        walking_distance=is_walking,
                        estimated_walking_time=walking_time
                    ))
        
        nearby.sort(key=lambda x: x.distance_km)
        return nearby[:limit]

# Singleton
_routing_service = None

def get_routing_service():
    global _routing_service
    if _routing_service is None:
        _routing_service = RoutingService()
    return _routing_service