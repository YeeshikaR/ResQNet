from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import current_user, db_connection, require_roles
from backend.queries.emergency_queries import get_emergencies, get_emergency, insert_emergency, update_status
from backend.schemas import EmergencyCreate
from backend.services.map_service import address_to_coords
from backend.services.priority_service import calculate_priority

router = APIRouter(prefix='/emergencies', tags=['emergencies'])


@router.post('', status_code=201)
def report_emergency(payload: EmergencyCreate, user=Depends(current_user), connection=Depends(db_connection)):
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
        return get_emergencies(connection, 'reported', None) + get_emergencies(connection, 'assigned', None)
    return get_emergencies(connection, status)


@router.patch('/{emergency_id}/resolve')
def resolve_emergency(emergency_id: int, user=Depends(require_roles('operator', 'admin')), connection=Depends(db_connection)):
    if not get_emergency(connection, emergency_id):
        raise HTTPException(status_code=404, detail='Emergency not found')
    update_status(connection, emergency_id, 'resolved')
    return {'message': 'Emergency resolved'}
