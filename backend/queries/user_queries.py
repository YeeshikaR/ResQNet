def get_user_by_email(connection, email: str):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        return cursor.fetchone()


def get_user_by_id(connection, user_id: int):
    with connection.cursor() as cursor:
        cursor.execute('SELECT user_id, name, email, role FROM users WHERE user_id = %s', (user_id,))
        return cursor.fetchone()


def insert_user(connection, name: str, email: str, password_hash: str, role: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            'INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)',
            (name, email, password_hash, role),
        )
        user_id = cursor.lastrowid
    connection.commit()
    return user_id
