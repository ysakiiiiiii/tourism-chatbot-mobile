"""
Comprehensive coordinates and transport data for Ilocos Norte
Includes accurate location data, transport routes, and detailed descriptions
"""

# Major hubs/terminals and landmarks with accurate coordinates
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
    "Vintar": {"lat": 18.0833, "lon": 120.5833},
    "Solsona": {"lat": 18.0333, "lon": 120.6167},
    "Nueva Era": {"lat": 18.1333, "lon": 120.7333},
    
    # Major Terminals
    "Laoag City Terminal": {"lat": 18.1950, "lon": 120.5920},
    "Batac Terminal": {"lat": 18.0550, "lon": 120.5640},
    "Pagudpud Terminal": {"lat": 18.5660, "lon": 120.7830},
    "Paoay Terminal": {"lat": 18.0540, "lon": 120.5280},
    
    # Tourist Attractions - Beaches
    "Saud Beach": {"lat": 18.5800, "lon": 120.8200},
    "Blue Lagoon": {"lat": 18.5850, "lon": 120.8250},
    "Maira-ira Beach": {"lat": 18.5500, "lon": 120.8100},
    "Sand Dunes": {"lat": 18.0600, "lon": 120.5100},
    
    # Tourist Attractions - Historical/Religious Sites
    "Paoay Church": {"lat": 18.0547, "lon": 120.5281},
    "Vigan Cathedral": {"lat": 17.5750, "lon": 120.3870},
    "Fort Ilocandia": {"lat": 18.2500, "lon": 120.7000},
    
    # Tourist Attractions - Natural Wonders
    "Kapurpurawan Rock": {"lat": 18.5350, "lon": 120.6480},
    "Kabigan Falls": {"lat": 18.5780, "lon": 120.8150},
    "Kaangrian Falls": {"lat": 18.5500, "lon": 120.6700},
    "Madarang Valley": {"lat": 18.0500, "lon": 120.4500},
    
    # Tourist Attractions - Museums & Heritage
    "Museo Ilocos Norte": {"lat": 18.1980, "lon": 120.5940},
    "Museo Nina Juan Apolinario": {"lat": 18.0550, "lon": 120.5650},
    "La Virgen Milagrosa Church": {"lat": 18.3500, "lon": 120.6800},
    
    # Dining & Culinary Destinations
    "Marcos Memorial Complex": {"lat": 18.3333, "lon": 120.6833},
    "Ilocos Norte Convention Center": {"lat": 18.1900, "lon": 120.5900},
}

# Transport routes with fares (₱ Philippine Peso) - Improved coverage
TRANSPORT_ROUTES = {
    # Jeepney routes - Comprehensive network
    "jeepney": {
        # Laoag connections
        ("Laoag", "Batac"): {"fare": 25, "time_minutes": 30, "distance_km": 18},
        ("Batac", "Laoag"): {"fare": 25, "time_minutes": 30, "distance_km": 18},
        ("Laoag", "Paoay"): {"fare": 20, "time_minutes": 25, "distance_km": 15},
        ("Paoay", "Laoag"): {"fare": 20, "time_minutes": 25, "distance_km": 15},
        ("Laoag", "Currimao"): {"fare": 30, "time_minutes": 40, "distance_km": 25},
        ("Currimao", "Laoag"): {"fare": 30, "time_minutes": 40, "distance_km": 25},
        ("Laoag", "San Nicolas"): {"fare": 35, "time_minutes": 45, "distance_km": 28},
        ("San Nicolas", "Laoag"): {"fare": 35, "time_minutes": 45, "distance_km": 28},
        
        # Batac connections
        ("Batac", "Paoay"): {"fare": 15, "time_minutes": 20, "distance_km": 10},
        ("Paoay", "Batac"): {"fare": 15, "time_minutes": 20, "distance_km": 10},
        ("Batac", "Piddig"): {"fare": 40, "time_minutes": 50, "distance_km": 32},
        ("Piddig", "Batac"): {"fare": 40, "time_minutes": 50, "distance_km": 32},
        
        # Northern routes (Pagudpud)
        ("Laoag", "Pagudpud"): {"fare": 80, "time_minutes": 120, "distance_km": 85},
        ("Pagudpud", "Laoag"): {"fare": 80, "time_minutes": 120, "distance_km": 85},
        ("Batac", "Pagudpud"): {"fare": 70, "time_minutes": 100, "distance_km": 70},
        ("Pagudpud", "Batac"): {"fare": 70, "time_minutes": 100, "distance_km": 70},
        ("Burgos", "Pagudpud"): {"fare": 50, "time_minutes": 60, "distance_km": 45},
        ("Pagudpud", "Burgos"): {"fare": 50, "time_minutes": 60, "distance_km": 45},
        
        # Additional municipal routes
        ("Laoag", "Vintar"): {"fare": 25, "time_minutes": 30, "distance_km": 20},
        ("Vintar", "Laoag"): {"fare": 25, "time_minutes": 30, "distance_km": 20},
        ("Laoag", "Sarrat"): {"fare": 35, "time_minutes": 45, "distance_km": 28},
        ("Sarrat", "Laoag"): {"fare": 35, "time_minutes": 45, "distance_km": 28},
    },
    
    # Tricycle (for short distances within municipality)
    "tricycle": {
        "base_fare": 15,
        "per_km": 10,
        "max_distance_km": 5,
    },
    
    # Bus (for longer inter-provincial distances)
    "bus": {
        ("Laoag", "Vigan"): {"fare": 100, "time_minutes": 90, "distance_km": 75},
        ("Vigan", "Laoag"): {"fare": 100, "time_minutes": 90, "distance_km": 75},
        ("Laoag", "Pagudpud"): {"fare": 120, "time_minutes": 90, "distance_km": 85},
        ("Pagudpud", "Laoag"): {"fare": 120, "time_minutes": 90, "distance_km": 85},
        ("Batac", "Vigan"): {"fare": 90, "time_minutes": 75, "distance_km": 60},
        ("Vigan", "Batac"): {"fare": 90, "time_minutes": 75, "distance_km": 60},
    },
    
    # Van (premium alternative for longer trips - faster)
    "van": {
        ("Laoag", "Pagudpud"): {"fare": 150, "time_minutes": 75, "distance_km": 85},
        ("Pagudpud", "Laoag"): {"fare": 150, "time_minutes": 75, "distance_km": 85},
        ("Laoag", "Vigan"): {"fare": 120, "time_minutes": 75, "distance_km": 75},
        ("Vigan", "Laoag"): {"fare": 120, "time_minutes": 75, "distance_km": 75},
        ("Batac", "Pagudpud"): {"fare": 140, "time_minutes": 70, "distance_km": 70},
        ("Pagudpud", "Batac"): {"fare": 140, "time_minutes": 70, "distance_km": 70},
    }
}

# Location descriptions for better context
LOCATION_DESCRIPTIONS = {
    "Laoag": [
        "Capital city of Ilocos Norte",
        "Home to the famous Paoay Church nearby",
        "Hub for most transportation in the province",
        "Known for salt production and agriculture",
        "Gateway to Ilocos Norte tourism",
        "Rich in Spanish colonial architecture",
        "Famous for local delicacies like longganisa",
        "Center of commerce and trade",
        "Beautiful city with historic landmarks",
        "Starting point for most tourist routes"
    ],
    "Batac": [
        "Birthplace of former Philippine president Ferdinand Marcos",
        "Home to the Marcos Presidential Center",
        "Gateway to northern Ilocos attractions",
        "Known for traditional local crafts",
        "Historical city with cultural significance",
        "Close to famous tourist destinations",
        "Center of agricultural activity",
        "Important transportation hub",
        "Rich Spanish colonial heritage",
        "Perfect base for exploring northern routes"
    ],
    "Pagudpud": [
        "Northernmost municipality of Ilocos Norte",
        "Known for pristine beaches and turquoise waters",
        "Home to famous Saud Beach",
        "Gateway to adventure sports and water activities",
        "Popular destination for summer beach trips",
        "Known for coconut trees and beach resorts",
        "Perfect for swimming and water sports",
        "Beautiful sunset views and romantic spots",
        "Ideal for family vacations",
        "Emerging eco-tourism destination"
    ],
    "Paoay": [
        "Famous for the UNESCO World Heritage Paoay Church",
        "Historical religious site attracting pilgrims",
        "Beautiful town with Spanish architecture",
        "Known for Paoay Lake nearby",
        "Cultural and spiritual destination",
        "Popular among history enthusiasts",
        "Home to local festivals and celebrations",
        "Gateway to heritage tourism",
        "Rich in religious and cultural significance",
        "Must-visit destination for culture seekers"
    ],
    "Burgos": [
        "Scenic coastal municipality",
        "Known for its beautiful seaside landscapes",
        "Gateway to Pagudpud attractions",
        "Home to historic churches and monuments",
        "Popular among adventure seekers",
        "Known for local handicrafts and weaving",
        "Beautiful views of Philippine Sea",
        "Peaceful and quiet municipality",
        "Great for nature and landscape photography",
        "Hidden gem of northern Ilocos"
    ],
    "Currimao": [
        "Charming coastal town in Ilocos Norte",
        "Known for peaceful beaches and coves",
        "Popular diving and snorkeling destination",
        "Home to marine sanctuaries",
        "Beautiful coastal scenery and views",
        "Ideal for water sports enthusiasts",
        "Known for fresh seafood",
        "Quiet and relaxing atmosphere",
        "Perfect for eco-tourism activities",
        "Gateway to marine adventures"
    ],
    "San Nicolas": [
        "Historic municipality with colonial architecture",
        "Known for religious sites and pilgrimages",
        "Home to traditional local industries",
        "Beautiful town with friendly locals",
        "Gateway to agricultural areas",
        "Known for local products and crafts",
        "Cultural heritage and traditions preserved",
        "Peaceful and family-friendly destination",
        "Good base for rural tourism",
        "Center of local commerce and trade"
    ],
    "Sarrat": [
        "Small but charming municipality",
        "Known for rice fields and agriculture",
        "Gateway to mountain and highland areas",
        "Beautiful rural landscapes",
        "Known for local farming traditions",
        "Peaceful and quiet environment",
        "Good for agri-tourism activities",
        "Home to traditional crafts",
        "Family-friendly destination",
        "Authentic provincial experience"
    ],
    "Piddig": [
        "Municipality known for archaeological significance",
        "Home to historical sites and museums",
        "Gateway to cultural tourism",
        "Known for heritage preservation",
        "Rich in indigenous history",
        "Beautiful heritage sites to explore",
        "Important for history enthusiasts",
        "Known for traditional pottery",
        "Center of cultural preservation",
        "Educational destination for history lovers"
    ],
    "Vigan": [
        "UNESCO World Heritage City",
        "Famous for well-preserved Spanish colonial architecture",
        "Capital city of Ilocos Sur",
        "Known as the Asian Mediterranean",
        "Popular tourist destination with history",
        "Home to famous cobblestone streets",
        "Center of cultural and heritage tourism",
        "Known for local handicrafts and antiques",
        "Perfect for heritage city tours",
        "Must-visit destination in northern Luzon"
    ]
}

# Walking speed and thresholds
WALKING_SPEED_KMH = 5  # Average walking speed
WALKING_DISTANCE_THRESHOLD_KM = 1.0  # Consider walking if less than 1km

# Fare calculation functions
def calculate_tricycle_fare(distance_km):
    """
    Calculate tricycle fare based on distance
    Base fare: ₱15, then ₱10 per km
    """
    base = TRANSPORT_ROUTES["tricycle"]["base_fare"]
    per_km = TRANSPORT_ROUTES["tricycle"]["per_km"]
    fare = base + (distance_km * per_km)
    return round(fare, 2)

def calculate_jeepney_fare(distance_km):
    """
    Calculate jeepney fare based on distance
    Base fare: ₱12 for first 4km
    Additional: ₱1.50 per km after 4km
    """
    if distance_km <= 4:
        return 12.00
    else:
        additional = (distance_km - 4) * 1.5
        return round(12 + additional, 2)

def calculate_van_fare(distance_km):
    """
    Calculate van fare based on distance
    Base fare: ₱20 for first 5km
    Additional: ₱2.00 per km after 5km (premium service)
    """
    if distance_km <= 5:
        return 20.00
    else:
        additional = (distance_km - 5) * 2.0
        return round(20 + additional, 2)

def calculate_bus_fare(distance_km):
    """
    Calculate bus fare based on distance
    Base fare: ₱18 for first 5km
    Additional: ₱1.80 per km after 5km
    """
    if distance_km <= 5:
        return 18.00
    else:
        additional = (distance_km - 5) * 1.8
        return round(18 + additional, 2)

def get_location_description(location_name):
    """Get a list of descriptions for a location"""
    return LOCATION_DESCRIPTIONS.get(location_name, ["Unknown location"])