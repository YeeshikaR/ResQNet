from fastapi import APIRouter, Depends, HTTPException
from pymysql.err import IntegrityError

from backend.dependencies import db_connection, require_roles
from backend.queries.dispatch_queries import get_dispatch_report, insert_dispatch
from backend.queries.emergency_queries import get_emergency
from backend.queries.resource_queries import get_resources, insert_resource
from backend.schemas import ResourceCreate
from backend.services.allocation_service import choose_resource
from backend.services.map_service import build_map_url

router = APIRouter(tags=['resources'])


@router.get('/resources')
def list_resources(available_only: bool = False, user=Depends(require_roles('operator', 'admin')), connection=Depends(db_connection)):
    return get_resources(connection, available_only)


@router.post('/resources', status_code=201)
def add_resource(payload: ResourceCreate, user=Depends(require_roles('admin')), connection=Depends(db_connection)):
    resource_id = insert_resource(connection, payload.model_dump())
    return {'resource_id': resource_id, 'message': 'Resource added'}


@router.post('/emergencies/{emergency_id}/dispatch')
def dispatch(emergency_id: int, user=Depends(require_roles('operator', 'admin')), connection=Depends(db_connection)):
    emergency = get_emergency(connection, emergency_id)
    if not emergency:
        raise HTTPException(status_code=404, detail='Emergency not found')
    if emergency['status'] != 'reported':
        raise HTTPException(status_code=409, detail='Emergency is not awaiting dispatch')
    try:
        resource, distance_km = choose_resource(emergency, get_resources(connection, available_only=True))
        dispatch_id = insert_dispatch(connection, emergency_id, resource['resource_id'], distance_km)
    except (ValueError, IntegrityError) as error:
        connection.rollback()
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {'dispatch_id': dispatch_id, 'resource': resource, 'distance_km': round(distance_km, 2)}


@router.get('/dispatches')
def dispatches(user=Depends(require_roles('operator', 'admin')), connection=Depends(db_connection)):
    return get_dispatch_report(connection)


@router.get('/map-url')
def map_url(user=Depends(require_roles('operator', 'admin')), connection=Depends(db_connection)):
    emergencies = get_emergencies(connection)
    resources = get_resources(connection)
    return {'url': build_map_url(emergencies, resources)}
