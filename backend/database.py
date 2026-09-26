from collections.abc import Generator

import pymysql
from pymysql.cursors import DictCursor

from backend.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=DictCursor,
        autocommit=False,
    )


def connection_scope() -> Generator[pymysql.connections.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
