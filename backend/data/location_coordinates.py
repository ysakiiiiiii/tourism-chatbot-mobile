"""
Coordinates and transport data for Ilocos Norte
You should update these with actual coordinates
"""

# Major hubs/terminals coordinates (approximate - update with real data)
LOCATION_COORDINATES = {
    # Major Cities/Municipalities
    "Laoag": {"lat": 18.1984, "lon": 120.5936},
    "Batac": {"lat": 18.0556, "lon": 120.5647},
    "Pagudpud": {"lat": 18.5667, "lon": 120.7833},
    "Vigan": {"lat": 17.5747, "lon": 120.3869},
    "Paoay": {"lat": 18.0556, "lon": 120.5281},
    "Burgos": {"lat": 18.5333, "lon": 120.6500},
    "Currimao": {"lat": 18.0167, "lon": 120.4833},
    "San Nicolas": {"lat": 18.1333, "lon": 120.6000},
    "Sarrat": {"lat": 18.1667, "lon": 120.6333},
    "Piddig": {"lat": 18.2000, "lon": 120.8000},
    "Pasquin": {"lat": 18.3333, "lon": 120.6167},
    
    # Specific landmarks (approximate - add more as needed)
    "Laoag City Terminal": {"lat": 18.1984, "lon": 120.5936},
    "Batac Terminal": {"lat": 18.0556, "lon": 120.5647},
    "Saud Beach": {"lat": 18.5800, "lon": 120.8200},
    "Paoay Church": {"lat": 18.0547, "lon": 120.5281},
    "Kapurpurawan Rock": {"lat": 18.5350, "lon": 120.6480},
}

# Transport routes with fares (₱ Philippine Peso)
TRANSPORT_ROUTES = {
    # Jeepney routes
    "jeepney": {
        ("Laoag", "Batac"): {"fare": 25, "time_minutes": 30},
        ("Batac", "Laoag"): {"fare": 25, "time_minutes": 30},
        ("Laoag", "Paoay"): {"fare": 20, "time_minutes": 25},
        ("Laoag", "Pagudpud"): {"fare": 80, "time_minutes": 120},
        ("Pagudpud", "Laoag"): {"fare": 80, "time_minutes": 120},
        ("Laoag", "Currimao"): {"fare": 30, "time_minutes": 40},
        ("Batac", "Paoay"): {"fare": 15, "time_minutes": 20},
    },
    
    # Tricycle (for short distances within municipality)
    "tricycle": {
        # Base fare + per km
        "base_fare": 15,
        "per_km": 10,
        "max_distance_km": 5,  # Tricycles usually for short trips
    },
    
    # Bus (for longer distances)
    "bus": {
        ("Laoag", "Vigan"): {"fare": 100, "time_minutes": 90},
        ("Vigan", "Laoag"): {"fare": 100, "time_minutes": 90},
        ("Laoag", "Pagudpud"): {"fare": 120, "time_minutes": 90},
    },
    
    # Van (alternative for longer trips)
    "van": {
        ("Laoag", "Pagudpud"): {"fare": 150, "time_minutes": 75},
        ("Laoag", "Vigan"): {"fare": 120, "time_minutes": 75},
    }
}

# Walking speed (average)
WALKING_SPEED_KMH = 5  # 5 km/h
WALKING_DISTANCE_THRESHOLD_KM = 1.0  # Consider walking if < 1km

# Fare calculation
def calculate_tricycle_fare(distance_km):
    """Calculate tricycle fare based on distance"""
    base = TRANSPORT_ROUTES["tricycle"]["base_fare"]
    per_km = TRANSPORT_ROUTES["tricycle"]["per_km"]
    return base + (distance_km * per_km)

def calculate_jeepney_fare(distance_km):
    """
    Calculate jeepney fare based on distance
    Base fare: ₱12 for first 4km
    Additional: ₱1.50 per km
    """
    if distance_km <= 4:
        return 12
    else:
        return 12 + ((distance_km - 4) * 1.5)