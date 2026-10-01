from backend.services.map_service import get_distance_km


def required_resource_type(emergency_type: str) -> str:
    return 'fire_truck' if emergency_type == 'fire' else 'ambulance'


def choose_resource(emergency: dict, resources: list[dict]) -> tuple[dict, float]:
    ranked = rank_resources(emergency, resources)
    if not ranked:
        target_type = required_resource_type(emergency['type'])
        raise ValueError(f'No available {target_type} found')
    resource = ranked[0]
    return resource, resource['distance_km']


def rank_resources(emergency: dict, resources: list[dict]) -> list[dict]:
    target_type = required_resource_type(emergency['type'])
    candidates = [
        resource for resource in resources
        if resource['status'] == 'available' and resource['type'] == target_type
    ]
    origin = (float(emergency['latitude']), float(emergency['longitude']))
    ranked = []
    for resource in candidates:
        distance = get_distance_km(origin, (float(resource['latitude']), float(resource['longitude'])))
        ranked.append({**resource, 'distance_km': distance})
    return sorted(ranked, key=lambda resource: resource['distance_km'])
