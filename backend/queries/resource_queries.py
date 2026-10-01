def get_resources(connection, available_only: bool = False):
    query = 'SELECT * FROM resources'
    if available_only:
        query += " WHERE status = 'available'"
    query += ' ORDER BY type, name'
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def insert_resource(connection, resource: dict) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            'INSERT INTO resources (type, name, latitude, longitude) VALUES (%s, %s, %s, %s)',
            (resource['type'], resource['name'], resource['latitude'], resource['longitude']),
        )
        resource_id = cursor.lastrowid
    connection.commit()
    return resource_id


def get_resource(connection, resource_id: int):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM resources WHERE resource_id = %s', (resource_id,))
        return cursor.fetchone()


def release_resource(connection, resource_id: int) -> bool:
    with connection.cursor() as cursor:
        cursor.execute('SELECT resource_id FROM resources WHERE resource_id = %s', (resource_id,))
        if not cursor.fetchone():
            return False
        cursor.execute(
            "UPDATE resources SET status = 'available' WHERE resource_id = %s",
            (resource_id,),
        )
        cursor.execute(
            """
            UPDATE emergencies e
            JOIN dispatches d ON d.emergency_id = e.emergency_id
            SET e.status = 'resolved'
            WHERE d.resource_id = %s AND e.status = 'assigned'
            """,
            (resource_id,),
        )
    connection.commit()
    return True
