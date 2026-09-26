from backend.services.map_service import get_distance_km


def required_resource_type(emergency_type: str) -> str:
    return 'fire_truck' if emergency_type == 'fire' else 'ambulance'


def choose_resource(emergency: dict, resources: list[dict]) -> tuple[dict, float]:
    target_type = required_resource_type(emergency['type'])
    candidates = [
        resource for resource in resources
        if resource['status'] == 'available' and resource['type'] == target_type
    ]
    if not candidates:
        raise ValueError(f'No available {target_type} found')
    origin = (float(emergency['latitude']), float(emergency['longitude']))
    ranked = []
    for resource in candidates:
        distance = get_distance_km(origin, (float(resource['latitude']), float(resource['longitude'])))
        ranked.append((distance, resource))
    distance, resource = min(ranked, key=lambda item: item[0])
    return resource, distance
