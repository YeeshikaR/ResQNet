from math import asin, cos, radians, sin, sqrt
import re

import requests

from backend.config import GEOAPIFY_API_KEY


def address_to_coords(address: str) -> tuple[float, float]:
    match = re.fullmatch(r'\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*', address)
    if match:
        latitude, longitude = float(match.group(1)), float(match.group(2))
        if -90 <= latitude <= 90 and -180 <= longitude <= 180:
            return latitude, longitude
    if not GEOAPIFY_API_KEY:
        raise ValueError('GEOAPIFY_API_KEY is not configured. Use "latitude,longitude" for local testing.')
    response = requests.get(
        'https://api.geoapify.com/v1/geocode/search',
        params={'text': address, 'apiKey': GEOAPIFY_API_KEY, 'limit': 1},
        timeout=15,
    )
    response.raise_for_status()
    features = response.json().get('features', [])
    if not features:
        raise ValueError(f'No location found for address: {address}')
    longitude, latitude = features[0]['geometry']['coordinates']
    return float(latitude), float(longitude)


def get_distance_km(origin: tuple[float, float], destination: tuple[float, float]) -> float:
    if not GEOAPIFY_API_KEY:
        return _haversine_km(origin, destination) * 1.25
    response = requests.get(
        'https://api.geoapify.com/v1/routing',
        params={
            'waypoints': f'{origin[0]},{origin[1]}|{destination[0]},{destination[1]}',
            'mode': 'drive',
            'apiKey': GEOAPIFY_API_KEY,
        },
        timeout=15,
    )
    response.raise_for_status()
    features = response.json().get('features', [])
    if not features:
        raise ValueError('Geoapify returned no route')
    return float(features[0]['properties']['distance']) / 1000


def build_map_url(emergencies: list[dict], resources: list[dict]) -> str | None:
    if not GEOAPIFY_API_KEY:
        return None
    markers = []
    for item in emergencies:
        markers.append(f'marker=lonlat:{item["longitude"]},{item["latitude"]};color:%23d94f4f;size:small')
    for item in resources:
        markers.append(f'marker=lonlat:{item["longitude"]},{item["latitude"]};color:%232f80ed;size:small')
    return 'https://maps.geoapify.com/v1/staticmap?' + '&'.join(
        [*markers, 'style:osm-bright-smooth', 'width:1000', 'height:600', f'apiKey={GEOAPIFY_API_KEY}']
    )


def _haversine_km(first: tuple[float, float], second: tuple[float, float]) -> float:
    latitude_one, longitude_one = map(radians, first)
    latitude_two, longitude_two = map(radians, second)
    delta_latitude = latitude_two - latitude_one
    delta_longitude = longitude_two - longitude_one
    value = sin(delta_latitude / 2) ** 2 + cos(latitude_one) * cos(latitude_two) * sin(delta_longitude / 2) ** 2
    return 6371 * 2 * asin(sqrt(value))
