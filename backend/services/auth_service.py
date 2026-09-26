from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from backend.config import JWT_ALGORITHM, JWT_SECRET

_passwords = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return _passwords.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _passwords.verify(password, password_hash)


def create_token(user: dict) -> str:
    payload = {
        'sub': str(user['user_id']),
        'role': user['role'],
        'name': user['name'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
