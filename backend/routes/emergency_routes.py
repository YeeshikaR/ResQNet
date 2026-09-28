from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import current_user, db_connection, require_roles
from backend.queries.dispatch_queries import complete_dispatch
from backend.queries.emergency_queries import get_emergencies, get_emergency, insert_emergency
from backend.schemas import EmergencyCreate
from backend.services.map_service import address_to_coords
from backend.services.priority_service import calculate_priority

router = APIRouter(prefix='/emergencies', tags=['emergencies'])


@router.post('', status_code=201)
def report_emergency(payload: EmergencyCreate, user=Depends(require_roles('citizen')), connection=Depends(db_connection)):
    try:
        latitude, longitude = address_to_coords(payload.address)
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    priority = calculate_priority(payload.severity, payload.people_affected)
    emergency_id = insert_emergency(connection, user['user_id'], payload.model_dump(), latitude, longitude, priority)
    return {'emergency_id': emergency_id, 'latitude': latitude, 'longitude': longitude, 'priority_score': priority}


@router.get('')
def list_emergencies(status: str | None = None, user=Depends(current_user), connection=Depends(db_connection)):
    if user['role'] == 'citizen':
        return get_emergencies(connection, status, reported_by=user['user_id'])
    if status is None:
        return list(get_emergencies(connection, 'reported', None)) + list(get_emergencies(connection, 'assigned', None))
    return get_emergencies(connection, status)


@router.patch('/{emergency_id}/resolve')
def resolve_emergency(emergency_id: int, user=Depends(current_user), connection=Depends(db_connection)):
    emergency = get_emergency(connection, emergency_id)
    if not emergency:
        raise HTTPException(status_code=404, detail='Emergency not found')
    if user['role'] == 'citizen' and emergency['reported_by'] != user['user_id']:
        raise HTTPException(status_code=403, detail='You can only complete your own emergency')
    if user['role'] not in {'citizen', 'operator', 'admin'}:
        raise HTTPException(status_code=403, detail='Insufficient permissions')
    if emergency['status'] != 'assigned':
        raise HTTPException(status_code=409, detail='Only an assigned emergency can be completed')
    resource_id = complete_dispatch(connection, emergency_id)
    if resource_id is None:
        raise HTTPException(status_code=409, detail='No resource is assigned to this emergency')
    return {'message': 'Task completed; resource is available again', 'resource_id': resource_id}
    resource_id = complete_dispatch(connection, emergency_id)
    if resource_id is None:
        raise HTTPException(status_code=409, detail='No resource is assigned to this emergency')
    return {'message': 'Task completed; resource is available again', 'resource_id': resource_id}
