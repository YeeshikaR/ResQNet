import os

import requests

API_URL = os.getenv('RESQNET_API_URL', 'http://localhost:8001').rstrip('/')


def request(method: str, path: str, token: str | None = None, **kwargs):
    headers = kwargs.pop('headers', {})
    if token:
        headers['Authorization'] = f'Bearer {token}'
    response = requests.request(method, f'{API_URL}{path}', headers=headers, timeout=20, **kwargs)
    if not response.ok:
        try:
            detail = response.json().get('detail', response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(detail)
    return response.json()


def login(email: str, password: str):
    return request('POST', '/login', json={'email': email, 'password': password})


def register(name: str, email: str, password: str):
    return request('POST', '/register', json={'name': name, 'email': email, 'password': password})


def emergencies(token: str, status: str | None = None):
    query = f'?status={status}' if status else ''
    return request('GET', f'/emergencies{query}', token)


def report(token: str, emergency: dict):
    return request('POST', '/emergencies', token, json=emergency)


def resources(token: str, available_only: bool = False):
    return request('GET', f'/resources?available_only={str(available_only).lower()}', token)


def add_resource(token: str, resource: dict):
    return request('POST', '/resources', token, json=resource)


def dispatch(token: str, emergency_id: int):
    return request('POST', f'/emergencies/{emergency_id}/dispatch', token)


def resolve(token: str, emergency_id: int):
    return request('PATCH', f'/emergencies/{emergency_id}/resolve', token)


def dispatches(token: str):
    return request('GET', '/dispatches', token)


def map_url(token: str):
    return request('GET', '/map-url', token).get('url')
