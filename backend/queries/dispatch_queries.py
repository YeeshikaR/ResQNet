def insert_dispatch(connection, emergency_id: int, resource_id: int, distance_km: float) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            'INSERT INTO dispatches (emergency_id, resource_id, distance_km) VALUES (%s, %s, %s)',
            (emergency_id, resource_id, distance_km),
        )
        dispatch_id = cursor.lastrowid
    connection.commit()
    return dispatch_id


def get_dispatch_report(connection):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT d.dispatch_id, d.dispatched_at, d.distance_km,
                   e.emergency_id, e.type AS emergency_type, e.severity,
                   r.resource_id, r.name AS resource_name, r.type AS resource_type
            FROM dispatches d
            JOIN emergencies e ON d.emergency_id = e.emergency_id
            JOIN resources r ON d.resource_id = r.resource_id
            ORDER BY d.dispatched_at DESC
        ''')
        return cursor.fetchall()


def complete_dispatch(connection, emergency_id: int) -> int | None:
    with connection.cursor() as cursor:
        cursor.execute('SELECT resource_id FROM dispatches WHERE emergency_id = %s', (emergency_id,))
        dispatch = cursor.fetchone()
        if not dispatch:
            return None
        cursor.execute(
            'UPDATE resources SET status = \'available\' WHERE resource_id = %s',
            (dispatch['resource_id'],),
        )
        cursor.execute(
            'UPDATE emergencies SET status = \'resolved\' WHERE emergency_id = %s',
            (emergency_id,),
        )
    connection.commit()
    return dispatch['resource_id']
