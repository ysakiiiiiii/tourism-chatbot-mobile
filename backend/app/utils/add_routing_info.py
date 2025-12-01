def add_routing_info(items):
    """Add routing availability info to items"""
    from app.services.routing_service import get_routing_service
    
    routing_service = get_routing_service()
    
    for item in items:
        # Check if this destination has coordinates
        coords = routing_service.get_destination_coordinates(item.get('id', ''))
        item['has_routing'] = coords is not None
        item['destination_id'] = item.get('id', '')
    
    return items