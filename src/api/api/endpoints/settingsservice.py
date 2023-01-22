from zoneinfo import available_timezones
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from api.auth import require_logged_in
from api.db import connect_db
import aiosqlite

LANGUAGES = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja']
COLOR_SCHEMES = ['light', 'dark']
TIMEZONES = available_timezones()

@require_logged_in
async def get_settings(request: Request) -> JSONResponse:
    """ Get the current user's settings. Supports filter query param to get only specified values.
        Multiple filters should be separated by commas.
    """
    user_id = request.state.user_id

    async with connect_db() as db:
        db.row_factory = aiosqlite.Row # allows the selected row to be casted as a dict where keys are column names
        async with db.execute("""SELECT user_id, avatar, discord_tag, about_me, language, 
            color_scheme, timezone FROM user_settings WHERE user_id = ?""", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return JSONResponse({'error': 'No user settings found'}, status_code=404)
            
    row_as_dict = dict(row)
    
    if 'filter' in request.query_params:
        filter_keys = [k.strip() for k in request.query_params['filter'].split(',')]
        return JSONResponse({k: v for k, v in row_as_dict.items() if k in filter_keys})

    return JSONResponse(row_as_dict)

@require_logged_in
async def edit_settings(request: Request) -> JSONResponse:
    """ Edit one or more settings for the current user """
    user_id = request.state.user_id
    body = await request.json()
    body['user_id'] = 10

    # check to make sure non-null settings are valid
    if 'language' in body.keys() and body['language'] not in LANGUAGES:
        return JSONResponse({'error': f"Unknown language: {body['language']}"}, status_code=400)
    if 'color_scheme' in body.keys() and body['color_scheme'] not in COLOR_SCHEMES:
        return JSONResponse({'error': f"Unknown color scheme: {body['color_scheme']}"}, status_code=400)
    if 'timezone' in body.keys() and body['timezone'] not in TIMEZONES:
            return JSONResponse({'error': f"Unknown timezone: {body['timezone']}"}, status_code=400)

    # only update the settings found in the request body
    set_clauses = [f'{key} = :{key}' for key in body.keys() if key != 'user_id']
    async with connect_db() as db:
        try:
            async with db.execute(f"UPDATE user_settings SET {','.join(set_clauses)} WHERE user_id = :user_id", body) as cursor:
                if cursor.rowcount == 0:
                    return JSONResponse({'error': 'Failed to update settings'}, status_code=500)
            await db.commit()
        except aiosqlite.OperationalError:
            return JSONResponse({'error': "body contains one or more invalid settings"}, status_code=400)
        except Exception as e:
            return JSONResponse({'error': 'Unexpected error'}, status_code=500)

    del body['user_id']
    resp = JSONResponse({'updated settings': body})
    
    if 'language' in body.keys():
        resp.set_cookie('language', body['language'])
    if 'color_scheme' in body.keys():
        resp.set_cookie('color_scheme', body['color_scheme'])

    return resp

routes = [
    Route('/api/user/settings', get_settings),
    Route('/api/user/settings/edit', edit_settings, methods=["POST"]),
]