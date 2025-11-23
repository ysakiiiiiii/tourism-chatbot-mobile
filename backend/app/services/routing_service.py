"""
Routing and navigation service for tourists
Calculates routes, fares, and provides turn-by-turn directions
"""
import math
from typing import List, Tuple, Optional
import pandas as pd
from app.config import EXCEL_FILE
from data.location_coordinates import (
    LOCATION_COORDINATES,
    TRANSPORT_ROUTES,
    WALKING_SPEED_KMH,
    WALKING_DISTANCE_THRESHOLD_KM,
    calculate_tricycle_fare,
    calculate_jeepney_fare
)
from app.models.location_schemas import (
    RouteStep, RouteResponse, NearbyPlace, TransportMode
)

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
        
        terminals = {k: v for k, v in LOCATION_COORDINATES.items() if 'Terminal' in k or k in ['Laoag', 'Batac', 'Pagudpud']}
        
        for terminal_name, coords in terminals.items():
            distance = self.haversine_distance(lat, lon, coords['lat'], coords['lon'])
            if distance < min_distance:
                min_distance = distance
                nearest_terminal = terminal_name
        
        return nearest_terminal, min_distance
    
    def calculate_route(
        self, 
        from_lat: float, 
        from_lon: float, 
        destination_id: str
    ) -> Optional[RouteResponse]:
        """
        Calculate the best route from user's location to destination
        """
        # Get destination info
        dest_coords = self.get_destination_coordinates(destination_id)
        if not dest_coords:
            return None
        
        dest_lat, dest_lon, dest_location = dest_coords
        
        # Get destination name
        dest_item = self.excel_df[self.excel_df['id'] == destination_id].iloc[0]
        dest_name = dest_item['name']
        
        # Calculate total distance
        total_distance = self.haversine_distance(from_lat, from_lon, dest_lat, dest_lon)
        
        steps = []
        warnings = []
        total_fare = 0
        total_time = 0
        step_num = 1
        
        # Step 1: If within walking distance
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
            # Step 1: Walk to nearest terminal
            nearest_terminal, terminal_distance = self.find_nearest_terminal(from_lat, from_lon)
            
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
                # Take tricycle to terminal
                tricycle_fare = calculate_tricycle_fare(terminal_distance)
                tricycle_time = int(terminal_distance * 5)  # Rough estimate
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take a tricycle to {nearest_terminal}",
                    transport_mode=TransportMode.TRICYCLE,
                    from_location="Your current location",
                    to_location=nearest_terminal,
                    distance_km=round(terminal_distance, 2),
                    fare=tricycle_fare,
                    estimated_time_minutes=tricycle_time,
                    landmark="Tell the driver to take you to the terminal"
                ))
                total_fare += tricycle_fare
                total_time += tricycle_time
                step_num += 1
            
            # Step 2: Take jeepney/bus to destination area
            route_key = self._find_transport_route(nearest_terminal, dest_location)
            
            if route_key:
                transport_mode, route_info = route_key
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take a {transport_mode} from {nearest_terminal} to {dest_location}",
                    transport_mode=TransportMode(transport_mode),
                    from_location=nearest_terminal,
                    to_location=dest_location,
                    distance_km=round(total_distance - terminal_distance, 2),
                    fare=route_info['fare'],
                    estimated_time_minutes=route_info['time_minutes'],
                    landmark=f"Look for {transport_mode}s going to {dest_location}"
                ))
                total_fare += route_info['fare']
                total_time += route_info['time_minutes']
                step_num += 1
            else:
                # Estimate fare if no direct route
                estimated_fare = calculate_jeepney_fare(total_distance)
                estimated_time = int((total_distance / 40) * 60)  # Assuming 40 km/h average
                steps.append(RouteStep(
                    step_number=step_num,
                    instruction=f"Take a jeepney from {nearest_terminal} towards {dest_location}",
                    transport_mode=TransportMode.JEEPNEY,
                    from_location=nearest_terminal,
                    to_location=dest_location,
                    distance_km=round(total_distance - terminal_distance, 2),
                    fare=estimated_fare,
                    estimated_time_minutes=estimated_time,
                    landmark=f"Ask the driver if they go to {dest_location}"
                ))
                total_fare += estimated_fare
                total_time += estimated_time
                step_num += 1
                warnings.append(f"No direct route found. Fare is estimated.")
            
            # Step 3: Final destination
            # Check if need to walk from drop-off point
            final_walk_instruction = f"You will arrive at {dest_name} in {dest_location}"
            steps.append(RouteStep(
                step_number=step_num,
                instruction=final_walk_instruction,
                transport_mode=TransportMode.WALKING,
                from_location=f"{dest_location} drop-off point",
                to_location=dest_name,
                distance_km=0,
                fare=0,
                estimated_time_minutes=0,
                landmark=f"Ask locals for {dest_name} - it's a well-known place!"
            ))
        
        return RouteResponse(
            destination_name=dest_name,
            destination_location=dest_location,
            total_distance_km=round(total_distance, 2),
            total_fare=round(total_fare, 2),
            total_time_minutes=total_time,
            steps=steps,
            warnings=warnings
        )
    
    def _find_transport_route(self, from_loc: str, to_loc: str) -> Optional[Tuple[str, dict]]:
        """
        Find available transport route between two locations
        Returns (transport_mode, route_info) or None
        """
        # Clean location names (remove "Terminal" suffix)
        from_clean = from_loc.replace(" Terminal", "").replace(" City", "")
        to_clean = to_loc.replace(" Terminal", "").replace(" City", "")
        
        # Check jeepney routes
        route = (from_clean, to_clean)
        if route in TRANSPORT_ROUTES['jeepney']:
            return ('jeepney', TRANSPORT_ROUTES['jeepney'][route])
        
        # Check bus routes
        if route in TRANSPORT_ROUTES['bus']:
            return ('bus', TRANSPORT_ROUTES['bus'][route])
        
        # Check van routes
        if route in TRANSPORT_ROUTES['van']:
            return ('van', TRANSPORT_ROUTES['van'][route])
        
        return None
    
    def find_nearby_places(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float = 5.0,
        limit: int = 10
    ) -> List[NearbyPlace]:
        """
        Find places near the user's location
        """
        nearby = []
        
        for _, item in self.excel_df.iterrows():
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
        
        # Sort by distance
        nearby.sort(key=lambda x: x.distance_km)
        
        return nearby[:limit]

# Singleton
_routing_service = None

def get_routing_service():
    global _routing_service
    if _routing_service is None:
        _routing_service = RoutingService()
    return _routing_service