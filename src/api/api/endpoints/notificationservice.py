from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import require_logged_in
from api.db import connect_db
from datetime import datetime, timezone

@require_logged_in
async def list_notifications(request: Request) -> JSONResponse:
    """ Get a list of notifications for the current user. Use one or more
        of the following query params to filter the results:
            - read: Get unread notifications if 0 or read notifications if 1
            - type: Get notifications that match the type. To query with
                    multiple types, separate them with commas.
            - before: Get notifications before a UTC POSIX timestamp
            - after: Get notifications after a UTC POSIX timestamp
    """
    user_id = request.state.user_id

    # construct WHERE clause based on request query_params
    where_clauses = ['n.user_id = ?']
    where_params  = [user_id]

    if 'read' in request.query_params:
        where_clauses.append('n.is_read = 0' if request.query_params['read'] == "0" else 'n.is_read = 1')
    if 'type' in request.query_params:
        try:
            types = list(map(int, request.query_params['type'].split(','))) # convert types to list of ints
            type_query = ['n.type = ?'] * len(types)
            where_clauses.append(f"({' OR '.join(type_query)})")
            where_params += types
        except Exception as e:
            return JSONResponse({'error': 'Bad type query'}, status_code=400)
    if 'before' in request.query_params:
        try:
            where_clauses.append('n.created_date < ?')
            where_params.append(datetime.fromtimestamp(float(request.query_params['before']), tz=timezone.utc).timestamp())
        except Exception as e:
            return JSONResponse({'error': 'Bad before date query'}, status_code=400)
    if 'after' in request.query_params:
        try:
            where_clauses.append('n.created_date > ?')
            where_params.append(datetime.fromtimestamp(float(request.query_params['after']), tz=timezone.utc).timestamp())
        except Exception as e:
            return JSONResponse({'error': 'Bad after date query'}, status_code=400)

    async with connect_db() as db:
        async with db.execute(f"""
            SELECT n.id, n.type, c.content, n.created_date, n.is_read FROM notifications n
            JOIN notification_content c ON n.content_id = c.id
            WHERE {' AND '.join(where_clauses)}""", tuple(where_params)) as cursor:

            notifs = [{
                'id': row[0], 
                'type': row[1], 
                'content': row[2], 
                'created_date': row[3], 
                'is_read': row[4] 
            } for row in await cursor.fetchall()]
            
    return JSONResponse({"notifications": notifs})

@require_logged_in
async def edit_single_read_status(request: Request) -> JSONResponse:
    """ Mark a single notification as either read or unread """

    body = await request.json()
    if 'is_read' not in body:
        return JSONResponse({'error': 'Missing key in body: is_read'}, status_code=400)

    is_read = 0 if body['is_read'] == 0 else 1
    notification_id = int(request.path_params['id'])
    user_id = request.state.user_id

    async with connect_db() as db:
        async with db.execute("""
            UPDATE notifications SET is_read = ?
            WHERE id = ? AND user_id = ?""", (is_read, notification_id, user_id)) as cursor:
        
            if cursor.rowcount == 1:
                await db.commit()
                return JSONResponse({'update_count': cursor.rowcount})

        # either the notification does not exist, or the request user_id does not match notif user_id
        async with db.execute("SELECT EXISTS (SELECT 1 FROM notifications WHERE id = ?)", (notification_id, )) as cursor:
            row = await cursor.fetchone()
            notification_exists = row is not None and bool(row[0])

    if notification_exists:
        return JSONResponse({'error': 'User does not have permission'}, status_code=401)
    return JSONResponse({'error': 'Unknown notification'}, status_code=404)
            
@require_logged_in
async def edit_all_read_status(request: Request) -> JSONResponse:
    """ Mark all notifications for the current user as either read or unread """

    body = await request.json()
    if 'is_read' not in body:
        return JSONResponse({'error': 'Missing key in body: is_read'}, status_code=400)

    is_read = 0 if body['is_read'] == 0 else 1
    user_id = request.state.user_id

    async with connect_db() as db:
        async with db.execute("UPDATE notifications SET is_read = ? WHERE user_id = ?", (is_read, user_id)) as cursor:
            count = cursor.rowcount
            if count > 0:
                await db.commit()

    return JSONResponse({'update_count': count})

@require_logged_in
async def get_unread_count(request: Request) -> JSONResponse:
    """ Get the number of unread notifications for the current user """

    user_id = request.state.user_id

    async with connect_db() as db:
        async with db.execute("""SELECT COUNT (*) FROM notifications WHERE user_id = ? AND is_read = 0""", (user_id, )) as cursor:
            row = await cursor.fetchone()
            count = row[0]

    return JSONResponse({'count': count})

routes = [
    Route('/api/notifications/list', list_notifications),
    Route('/api/notifications/edit/read_status/{id:int}', edit_single_read_status, methods=["POST"]),
    Route('/api/notifications/edit/read_status/all', edit_all_read_status, methods=["POST"]),
    Route('/api/notifications/unread_count', get_unread_count),
]