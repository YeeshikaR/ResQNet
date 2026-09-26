from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt

from backend.config import JWT_ALGORITHM, JWT_SECRET
from backend.database import get_connection
from backend.queries.user_queries import get_user_by_id


def db_connection():
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def current_user(authorization: str = Header(default=''), connection=Depends(db_connection)):
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Bearer token required')
    try:
        payload = jwt.decode(authorization[7:], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload['sub'])
    except (JWTError, KeyError, ValueError) as error:
        raise HTTPException(status_code=401, detail='Invalid or expired token') from error
    user = get_user_by_id(connection, user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User no longer exists')
    return user


def require_roles(*roles: str):
    def checker(user=Depends(current_user)):
        if user['role'] not in roles:
            raise HTTPException(status_code=403, detail='Insufficient permissions')
        return user
    return checker
