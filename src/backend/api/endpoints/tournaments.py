from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import connect_db, s3_wrapper, handle
from api.utils.responses import JSONResponse, bind_request_body
from common.auth import permissions
import json
from datetime import datetime
from common.data.models import (CreateTournamentRequestData)
from common.data.commands import (CreateTournamentCommand)

@bind_request_body(CreateTournamentRequestData)
#@require_permission(permissions.CREATE_TOURNAMENT)
async def create_tournament(request: Request, body: CreateTournamentRequestData) -> JSONResponse:
    command = CreateTournamentCommand(body)
    await handle(command)
    return JSONResponse({})

@require_permission(permissions.EDIT_TOURNAMENT)
async def edit_tournament(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    body = await request.json()
    try:
        tournament_name = body['name']
        series_id = body['series_id'] #might be None so don't convert to int
        registrations_open = int(body['registrations_open'])
        date_start = int(body['date_start'])
        date_end = int(body['date_end'])
        description = body['description']
        use_series_description = int(body['use_series_description'])
        series_stats_include = int(body['series_stats_include'])
        logo = body['logo']
        url = body['url']
        registration_deadline = body['registration_deadline']
        registration_cap = body['registration_cap']
        teams_allowed = int(body['teams_allowed'])
        teams_only = int(body['teams_only'])
        team_members_only = int(body['team_members_only'])
        min_squad_size = int(body['min_squad_size'])
        max_squad_size = int(body['max_squad_size'])
        squad_tag_required = int(body['squad_tag_required'])
        squad_name_required = int(body['squad_name_required'])
        mii_name_required = int(body['mii_name_required'])
        host_status_required = int(body['host_status_required'])
        checkins_open = int(body['checkins_open'])
        min_players_checkin = int(body['min_players_checkin'])
        verified_fc_required = int(body['verified_fc_required'])
        is_viewable = int(body['is_viewable'])
        is_public = int(body['is_public'])
        show_on_profiles = int(body['show_on_profiles'])
        # object storage-only fields
        ruleset = body['ruleset']
        use_series_ruleset = int(body['use_series_ruleset'])
        organizer = body['organizer']
        location = body['location']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)

    async with connect_db() as db:
        cursor = await db.execute("""UPDATE tournaments
            SET name = ?,
            series_id = ?,
            registrations_open = ?,
            date_start = ?,
            date_end = ?,
            description = ?,
            use_series_description = ?,
            series_stats_include = ?,
            logo = ?,
            url = ?,
            registration_deadline = ?,
            registration_cap = ?,
            teams_allowed = ?,
            teams_only = ?,
            team_members_only = ?,
            min_squad_size = ?,
            max_squad_size = ?,
            squad_tag_required = ?,
            squad_name_required = ?,
            mii_name_required = ?,
            host_status_required = ?,
            checkins_open = ?,
            min_players_checkin = ?,
            verified_fc_required = ?,
            is_viewable = ?,
            is_public = ?,
            show_on_profiles = ?
            WHERE id = ?""",
            (tournament_name, series_id, registrations_open, date_start, date_end, description, use_series_description, series_stats_include,
            logo, url, registration_deadline, registration_cap, teams_allowed, teams_only, team_members_only, min_squad_size,
            max_squad_size, squad_tag_required, squad_name_required, mii_name_required, host_status_required, checkins_open,
            min_players_checkin, verified_fc_required, is_viewable, is_public, show_on_profiles, tournament_id))
        updated_rows = cursor.rowcount
        if updated_rows == 0:
            return JSONResponse({'error':'No tournament found'}, status_code=404)
        await db.commit()

    body = await s3_wrapper.get_object('tournaments', f'{tournament_id}.json')
    if body is None:
        return JSONResponse({'error':'No tournament found'}, status_code=404)
    json_body = json.loads(body)
    json_body["name"] = tournament_name
    json_body["series_id"] = series_id
    json_body["registrations_open"] = registrations_open
    json_body["date_start"] = date_start
    json_body["date_end"] = date_end
    json_body["description"] = description
    json_body["use_series_description"] = use_series_description
    json_body["series_stats_include"] = series_stats_include
    json_body["logo"] = logo
    json_body["url"] = url
    json_body["registration_deadline"] = registration_deadline
    json_body["registration_cap"] = registration_cap
    json_body["teams_allowed"] = teams_allowed
    json_body["teams_only"] = teams_only
    json_body["team_members_only"] = team_members_only
    json_body["min_squad_size"] = min_squad_size
    json_body["max_squad_size"] = max_squad_size
    json_body["squad_tag_required"] = squad_tag_required
    json_body["squad_name_required"] = squad_name_required
    json_body["mii_name_required"] = mii_name_required
    json_body["host_status_required"] = host_status_required
    json_body["checkins_open"] = checkins_open
    json_body["min_players_checkin"] = min_players_checkin
    json_body["verified_fc_required"] = verified_fc_required
    json_body["is_viewable"] = is_viewable
    json_body["is_public"] = is_public
    json_body["show_on_profiles"] = show_on_profiles
    json_body["ruleset"] = ruleset
    json_body["use_series_ruleset"] = use_series_ruleset
    json_body["organizer"] = organizer
    json_body["location"] = location
    s3_message = bytes(json.dumps(json_body).encode('utf-8'))
    await s3_wrapper.put_object('tournaments', f'{tournament_id}.json', s3_message)
    return JSONResponse(json_body)

async def tournament_info(request: Request) -> JSONResponse:
    tournament_id = request.path_params['id']
    
    body = await s3_wrapper.get_object('tournaments', f'{tournament_id}.json')
    if body is None:
        return JSONResponse({'error':'No tournament found'}, status_code=404)
    json_body = json.loads(body)
    return JSONResponse(json_body)

async def tournament_list_minimal(where_clause, variable_parameters):
    async with connect_db() as db:
        async with db.execute(f"SELECT id, name, date_start, date_end, game FROM tournaments {where_clause}", variable_parameters) as cursor:
            rows = await cursor.fetchall()
    tournaments = []
    for row in rows:
        tournament = {
            'id': row[0],
            'name': row[1],
            'date_start': row[2],
            'date_end': row[3],
            'game': row[4],
        }
        tournaments.append(tournament)
    return JSONResponse({"tournaments": tournaments})

async def tournament_list_basic(where_clause, variable_parameters):
    async with connect_db() as db:
        async with db.execute(f"SELECT id, name, game, mode, series_id, is_squad, registrations_open, description, date_start, date_end, logo FROM tournaments {where_clause}", variable_parameters) as cursor:
            rows = await cursor.fetchall()
    tournaments = []
    for row in rows:
        tournament = {
            'id': row[0],
            'name': row[1],
            'game': row[2],
            'mode': row[3],
            'series_id': row[4],
            'is_squad': row[5],
            'registrations_open': row[6],
            'description': row[7],
            'date_start': row[8],
            'date_end': row[9],
            'logo': row[10]
        }
        tournaments.append(tournament)
    return JSONResponse({'tournaments': tournaments})

async def tournament_list(request:Request) -> JSONResponse:
    # constructing WHERE clause for SQLite query
    where_clauses = []
    variable_parameters = []
    if 'skipCompleted' in request.query_params:
        # a completed tournament is one where the ending date is in the past
        where_clauses.append("date_end > ?")
        variable_parameters.append(int(datetime.utcnow().timestamp()))
    if 'game' in request.query_params:
        where_clauses.append("game = ?")
        variable_parameters.append(request.query_params['game'].upper())
    if 'mode' in request.query_params:
        where_clauses.append("mode = ?")
        variable_parameters.append(request.query_params['mode'])
    if 'showPrivate' not in request.query_params:
        where_clauses.append("is_viewable = 1")
    if 'seriesId' in request.query_params:
        where_clauses.append("series_id = ?")
        variable_parameters.append(request.query_params['seriesId'])
    where_clause = ""
    if len(where_clauses) > 0:
        where_clause = f"WHERE {' AND '.join(where_clauses)}"
    if 'detail' in request.query_params:
        if request.query_params['detail'] == 'basic':
            return await tournament_list_basic(where_clause, tuple(variable_parameters))
    return await tournament_list_minimal(where_clause, tuple(variable_parameters))

@require_permission(permissions.CREATE_SERIES)
async def create_series(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        series_name = body['name']
        url = body['url']
        game = body['game']
        mode = body['mode']
        is_historical = int(body['is_historical'])
        is_public = int(body['is_public'])
        description = body['description']
        logo = body['logo']
        # object storage-only fields
        ruleset = body['ruleset']
        organizer = body['organizer']
        location = body['location']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'})

    # store minimal data about each series in the SQLite DB
    async with connect_db() as db:
        cursor = await db.execute(
            "INSERT INTO tournament_series(name, url, game, mode, is_historical, is_public, description, logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (series_name, url, game, mode, is_historical, is_public, description, logo))
        series_id = cursor.lastrowid
        await db.commit()

    # store more detailed information about the series in object storage
    s3_json = {"id": series_id,
                "name": series_name,
                "url": url,
                "game": game,
                "mode": mode,
                "is_historical": is_historical,
                "is_public": is_public,
                "description": description,
                "logo": logo,
                "ruleset": ruleset,
                "organizer": organizer,
                "location": location
                }

    s3_message = bytes(json.dumps(s3_json).encode('utf-8'))
    result = await s3_wrapper.put_object('series', f'{series_id}.json', s3_message)
    return JSONResponse(s3_json)

@require_permission(permissions.EDIT_SERIES)
async def edit_series(request: Request) -> JSONResponse:
    series_id = request.path_params['id']
    body = await request.json()
    try:
        series_name = body['name']
        url = body['url']
        game = body['game']
        mode = body['mode']
        is_historical = int(body['is_historical'])
        is_public = int(body['is_public'])
        description = body['description']
        logo = body['logo']
        # object storage-only fields
        ruleset = body['ruleset']
        organizer = body['organizer']
        location = body['location']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)
    async with connect_db() as db:
        cursor = await db.execute("""UPDATE tournament_series
            SET name = ?,
            url = ?,
            game = ?,
            mode = ?,
            is_historical = ?,
            is_public = ?,
            description = ?,
            logo = ?
            WHERE id = ?""",
            (series_name, url, game, mode, is_historical, is_public, description, logo, series_id))
        updated_rows = cursor.rowcount
        if updated_rows == 0:
            return JSONResponse({'error':'No tournament found'}, status_code=404)
        await db.commit()
    body = await s3_wrapper.get_object('series', f'{series_id}.json')
    if body is None:
        return JSONResponse({'error':'No tournament found'}, status_code=404)
    json_body = json.loads(body)
    json_body["name"] = series_name
    json_body["url"] = url
    json_body["game"] = game
    json_body["mode"] = mode
    json_body["is_historical"] = is_historical
    json_body["is_public"] = is_public
    json_body["description"] = description
    json_body["logo"] = logo
    json_body["ruleset"] = ruleset
    json_body["organizer"] = organizer
    json_body["location"] = location
    s3_message = bytes(json.dumps(json_body).encode('utf-8'))
    await s3_wrapper.put_object('series', f'{series_id}.json', s3_message)
    return JSONResponse(json_body)

async def series_info(request: Request) -> JSONResponse:
    series_id = request.path_params['id']
    body = await s3_wrapper.get_object('series', f'{series_id}.json')
    if body is None:
        return JSONResponse({'error':'No series found'}, status_code=404)
    json_body = json.loads(body)
    return JSONResponse(json_body)

async def series_list(request: Request) -> JSONResponse:
    # constructing WHERE clause for SQLite query
    where_clauses = []
    variable_parameters = []
    if 'showHistorical' not in request.query_params:
        where_clauses.append("is_historical = 0")
    if 'game' in request.query_params:
        where_clauses.append("game = ?")
        variable_parameters.append(request.query_params['game'].upper())
    if 'mode' in request.query_params:
        where_clauses.append("mode = ?")
        variable_parameters.append(request.query_params['mode'])
    if 'showPrivate' not in request.query_params:
        where_clauses.append("is_public = 1")
    where_clause = ""
    if len(where_clauses) > 0:
        where_clause = f"WHERE {' AND '.join(where_clauses)}"
    async with connect_db() as db:
        async with db.execute(f"SELECT id, name, url, game, mode, is_historical, is_public, description, logo FROM tournament_series {where_clause}", variable_parameters) as cursor:
            rows = await cursor.fetchall()
        series = []
        for row in rows:
            curr_series = {
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'game': row[3],
                'mode': row[4],
                'is_historical': row[5],
                'is_public': row[6],
                'description': row[7],
                'logo': row[8]
            }
            series.append(curr_series)
        return JSONResponse({'series': series})

@require_permission(permissions.CREATE_TOURNAMENT_TEMPLATE)
async def create_template(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        # database-only fields. we only need two of them since
        # other data from templates probably won't ever need to be used in queries.
        template_name = body['template_name']
        series_id = body['series_id'] #might be None so don't convert to int
        # object storage-only fields
        tournament_name = body['tournament_name']
        game = body['game']
        mode = body['mode']
        is_squad = int(body['is_squad'])
        registrations_open = int(body['registrations_open'])
        description = body['description']
        use_series_description = int(body['use_series_description'])
        series_stats_include = int(body['series_stats_include'])
        logo = body['logo']
        registration_deadline = body['registration_deadline']
        registration_cap = body['registration_cap']
        teams_allowed = int(body['teams_allowed'])
        teams_only = int(body['teams_only'])
        team_members_only = int(body['team_members_only'])
        min_squad_size = int(body['min_squad_size'])
        max_squad_size = int(body['max_squad_size'])
        squad_tag_required = int(body['squad_tag_required'])
        squad_name_required = int(body['squad_name_required'])
        mii_name_required = int(body['mii_name_required'])
        host_status_required = int(body['host_status_required'])
        checkins_open = int(body['checkins_open'])
        min_players_checkin = int(body['min_players_checkin'])
        verified_fc_required = int(body['verified_fc_required'])
        is_viewable = int(body['is_viewable'])
        is_public = int(body['is_public'])
        show_on_profiles = int(body['show_on_profiles'])
        ruleset = body['ruleset']
        use_series_ruleset = int(body['use_series_ruleset'])
        organizer = body['organizer']
        location = body['location']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)

    async with connect_db() as db:
        cursor = await db.execute("INSERT INTO tournament_templates (name, series_id) VALUES (?, ?)",
        (template_name, series_id))
        template_id = cursor.lastrowid
        await db.commit()

    # store more detailed information about the template in object storage
    s3_json = {"id": template_id,
                "template_name": template_name,
                "series_id": series_id,
                "tournament_name": tournament_name,
                "game": game,
                "mode": mode,
                "is_squad": is_squad,
                "registrations_open": registrations_open,
                "description": description,
                "use_series_description": use_series_description,
                "series_stats_include": series_stats_include,
                "logo": logo,
                "registration_deadline": registration_deadline,
                "registration_cap": registration_cap,
                "teams_allowed": teams_allowed,
                "teams_only": teams_only,
                "team_members_only": team_members_only,
                "min_squad_size": min_squad_size,
                "max_squad_size": max_squad_size,
                "squad_tag_required": squad_tag_required,
                "squad_name_required": squad_name_required,
                "mii_name_required": mii_name_required,
                "host_status_required": host_status_required,
                "checkins_open": checkins_open,
                "min_players_checkin": min_players_checkin,
                "verified_fc_required": verified_fc_required,
                "is_viewable": is_viewable,
                "is_public": is_public,
                "show_on_profiles": show_on_profiles,
                "ruleset": ruleset,
                "use_series_ruleset": use_series_ruleset,
                "organizer": organizer,
                "location": location
                }
    s3_message = bytes(json.dumps(s3_json).encode('utf-8'))
    await s3_wrapper.put_object('templates', f'{template_id}.json', s3_message)
    return JSONResponse(s3_json)

@require_permission(permissions.EDIT_TOURNAMENT_TEMPLATE)
async def edit_template(request: Request) -> JSONResponse:
    template_id = request.path_params['id']
    body = await request.json()
    try:
        # database-only fields. we only need two of them since
        # other data from templates probably won't ever need to be used in queries.
        template_name = body['template_name']
        series_id = body['series_id'] #might be None so don't convert to int
        # object storage-only fields
        tournament_name = body['tournament_name']
        game = body['game']
        mode = body['mode']
        is_squad = int(body['is_squad'])
        registrations_open = int(body['registrations_open'])
        description = body['description']
        use_series_description = int(body['use_series_description'])
        series_stats_include = int(body['series_stats_include'])
        logo = body['logo']
        registration_deadline = body['registration_deadline']
        registration_cap = body['registration_cap']
        teams_allowed = int(body['teams_allowed'])
        teams_only = int(body['teams_only'])
        team_members_only = int(body['team_members_only'])
        min_squad_size = int(body['min_squad_size'])
        max_squad_size = int(body['max_squad_size'])
        squad_tag_required = int(body['squad_tag_required'])
        squad_name_required = int(body['squad_name_required'])
        mii_name_required = int(body['mii_name_required'])
        host_status_required = int(body['host_status_required'])
        checkins_open = int(body['checkins_open'])
        min_players_checkin = int(body['min_players_checkin'])
        verified_fc_required = int(body['verified_fc_required'])
        is_viewable = int(body['is_viewable'])
        is_public = int(body['is_public'])
        show_on_profiles = int(body['show_on_profiles'])
        ruleset = body['ruleset']
        use_series_ruleset = int(body['use_series_ruleset'])
        organizer = body['organizer']
        location = body['location']
    except Exception as e:
        return JSONResponse({'error': 'No correct body send'}, status_code=400)

    async with connect_db() as db:
        cursor = await db.execute("""UPDATE tournament_templates
            SET name = ?,
            series_id = ?
            WHERE id = ?""", (template_name, series_id, template_id))
        updated_rows = cursor.rowcount
        if updated_rows == 0:
            return JSONResponse({'error':'No template found'}, status_code=404)
        await db.commit()

    body = await s3_wrapper.get_object('templates', f'{template_id}.json')
    if body is None:
        return JSONResponse({'error':'No template found'}, status_code=404)
    json_body = json.loads(body)
    json_body["template_name"] = template_name
    json_body["series_id"] = series_id
    json_body["tournament_name"] = tournament_name
    json_body["game"] = game
    json_body["mode"] = mode
    json_body["is_squad"] = is_squad
    json_body["registrations_open"] = registrations_open
    json_body["description"] = description
    json_body["use_series_description"] = use_series_description
    json_body["series_stats_include"] = series_stats_include
    json_body["logo"] = logo
    json_body["registration_deadline"] = registration_deadline
    json_body["registration_cap"] = registration_cap
    json_body["teams_allowed"] = teams_allowed
    json_body["teams_only"] = teams_only
    json_body["team_members_only"] = team_members_only
    json_body["min_squad_size"] = min_squad_size
    json_body["max_squad_size"] = max_squad_size
    json_body["squad_tag_required"] = squad_tag_required
    json_body["squad_name_required"] = squad_name_required
    json_body["mii_name_required"] = mii_name_required
    json_body["host_status_required"] = host_status_required
    json_body["checkins_open"] = checkins_open
    json_body["min_players_checkin"] = min_players_checkin
    json_body["verified_fc_required"] = verified_fc_required
    json_body["is_viewable"] = is_viewable
    json_body["is_public"] = is_public
    json_body["show_on_profiles"] = show_on_profiles
    json_body["ruleset"] = ruleset
    json_body["use_series_ruleset"] = use_series_ruleset
    json_body["organizer"] = organizer
    json_body["location"] = location
    s3_message = bytes(json.dumps(json_body).encode('utf-8'))
    await s3_wrapper.put_object('templates', f'{template_id}.json', s3_message)
    return JSONResponse(json_body)

async def template_info(request: Request) -> JSONResponse:
    template_id = request.path_params['id']
    body = await s3_wrapper.get_object('templates', f'{template_id}.json')
    if body is None:
        return JSONResponse({'error':'No template found'}, status_code=404)
    json_body = json.loads(body)
    return JSONResponse(json_body)

async def template_list(request: Request) -> JSONResponse:
    # constructing WHERE clause for SQLite query
    where_clauses = []
    variable_parameters = []
    if 'seriesId' in request.query_params:
        where_clauses.append("series_id = ?")
        variable_parameters.append(request.query_params['series_id'])
    where_clause = ""
    if len(where_clauses) > 0:
        where_clause = f"WHERE {' AND '.join(where_clauses)}"
    async with connect_db() as db:
        async with db.execute(f"SELECT id, name, series_id FROM tournament_templates {where_clause}", variable_parameters) as cursor:
            rows = await cursor.fetchall()
        templates = []
        for row in rows:
            template = {
                'id': row[0],
                'name': row[1],
                'series_id': row[2]
            }
            templates.append(template)
        return JSONResponse({'templates': templates})

routes = [
    Route('/api/tournaments/create', create_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}/edit', edit_tournament, methods=["POST"]),
    Route('/api/tournaments/{id:int}', tournament_info),
    Route('/api/tournaments/list', tournament_list),
    Route('/api/tournaments/series/create', create_series, methods=['POST']),
    Route('/api/tournaments/series/{id:int}/edit', edit_series, methods=['POST']),
    Route('/api/tournaments/series/{id:int}', series_info),
    Route('/api/tournaments/series/list', series_list),
    Route('/api/tournaments/templates/create', create_template, methods=['POST']),
    Route('/api/tournaments/templates/{id:int}/edit', edit_template, methods=['POST']),
    Route('/api/tournaments/templates/{id:int}', template_info),
    Route('/api/tournaments/templates/list', template_list)    
]