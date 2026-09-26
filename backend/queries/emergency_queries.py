def insert_emergency(connection, reported_by: int, emergency: dict, latitude: float, longitude: float, priority_score: float) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            '''INSERT INTO emergencies
               (reported_by, type, severity, people_affected, latitude, longitude, priority_score)
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (reported_by, emergency['type'], emergency['severity'], emergency['people_affected'], latitude, longitude, priority_score),
        )
        emergency_id = cursor.lastrowid
    connection.commit()
    return emergency_id


def get_emergencies(connection, status: str | None = None, reported_by: int | None = None):
    query = '''SELECT e.*, u.name AS reported_by_name,
                      d.dispatch_id, d.distance_km, d.dispatched_at,
                      r.resource_id AS assigned_resource_id,
                      r.name AS assigned_resource_name,
                      r.type AS assigned_resource_type,
                      r.status AS assigned_resource_status
               FROM emergencies e
               JOIN users u ON e.reported_by = u.user_id
               LEFT JOIN dispatches d ON d.emergency_id = e.emergency_id
               LEFT JOIN resources r ON r.resource_id = d.resource_id'''
    params = []
    filters = []
    if status:
        filters.append('e.status = %s')
        params.append(status)
    if reported_by is not None:
        filters.append('e.reported_by = %s')
        params.append(reported_by)
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY e.priority_score DESC, e.created_at ASC'
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def get_emergency(connection, emergency_id: int):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM emergencies WHERE emergency_id = %s', (emergency_id,))
        return cursor.fetchone()


def update_status(connection, emergency_id: int, status: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute('UPDATE emergencies SET status = %s WHERE emergency_id = %s', (status, emergency_id))
    connection.commit()
