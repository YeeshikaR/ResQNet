from fastapi import APIRouter, Depends, HTTPException
from pymysql.err import IntegrityError

from backend.dependencies import db_connection
from backend.queries.user_queries import get_user_by_email, insert_user
from backend.schemas import LoginRequest, RegisterRequest, TokenResponse
from backend.services.auth_service import create_token, hash_password, verify_password

router = APIRouter(tags=['auth'])

@router.post('/register', status_code=201)
def register(payload: RegisterRequest, connection=Depends(db_connection)):
    try:
        user_id = insert_user(connection, payload.name, payload.email.lower(), hash_password(payload.password), 'citizen')
    except IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=409, detail='Email is already registered') from error
    return {'user_id': user_id, 'message': 'Account created'}


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, connection=Depends(db_connection)):
    user = get_user_by_email(connection, payload.email.lower())
    if not user or not verify_password(payload.password, user['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    return {'access_token': create_token(user), 'token_type': 'bearer', 'role': user['role']}
