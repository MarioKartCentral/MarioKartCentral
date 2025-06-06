"""
Time trials API endpoints.
"""

from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands.time_trials import (
    CreateTimeTrialCommand, 
    GetTimeTrialCommand, 
    ListTimeTrialsCommand, 
    DeleteTimeTrialCommand
)
from common.data.models import (
    CreateTimeTrialRequestData,
    ListTimeTrialsRequestData,
    TimeTrialResponseData,
    Problem
)
from common.data.models.time_trials import validate_and_create_time_trial_data


@bind_request_body(CreateTimeTrialRequestData)
@require_permission(permissions.SUBMIT_TIME_TRIAL, check_denied_only=True)
async def create_time_trial(request: Request, body: CreateTimeTrialRequestData) -> JSONResponse:
    """Create a new time trial record."""
    # Get the authenticated user from request state
    user = request.state.user
    
    # Ensure user has a linked player account
    if not user.player_id:
        raise Problem("User must have a linked player account to submit time trials", status=400)
    
    # Validate and convert the data field to the appropriate schema type
    validated_data = validate_and_create_time_trial_data(body.data, body.game)
    
    command = CreateTimeTrialCommand(
        player_id=str(user.player_id),
        game=body.game,
        track=body.track,
        time_ms=body.time_ms,
        data=validated_data,
        proof_url=body.proof_url,
        description=body.description
    )
    
    time_trial = await handle(command)
    
    response_data = TimeTrialResponseData(
        id=time_trial.id,
        version=time_trial.version,
        player_id=time_trial.player_id,
        game=time_trial.game,
        track=time_trial.track,
        time_ms=time_trial.time_ms,
        data=time_trial.data,
        created_at=time_trial.created_at,
        updated_at=time_trial.updated_at,
        proof_url=time_trial.proof_url,
        description=time_trial.description
    )
    
    return JSONResponse(response_data.__dict__)


async def get_time_trial(request: Request) -> JSONResponse:
    """Get a specific time trial by ID."""
    trial_id = request.path_params['trial_id']
    
    command = GetTimeTrialCommand(trial_id=trial_id)
    time_trial = await handle(command)
    
    if time_trial is None:
        return JSONResponse({'error': 'Time trial not found'}, status_code=404)
    
    response_data = TimeTrialResponseData(
        id=time_trial.id,
        version=time_trial.version,
        player_id=time_trial.player_id,
        game=time_trial.game,
        track=time_trial.track,
        time_ms=time_trial.time_ms,
        data=time_trial.data,
        created_at=time_trial.created_at,
        updated_at=time_trial.updated_at,
        proof_url=time_trial.proof_url,
        description=time_trial.description
    )
    
    return JSONResponse(response_data.__dict__)


@bind_request_query(ListTimeTrialsRequestData)
async def list_time_trials(request: Request, query: ListTimeTrialsRequestData) -> JSONResponse:
    """List time trials with optional filters."""
    command = ListTimeTrialsCommand(
        player_id=query.player_id,
        game=query.game,
        track=query.track,
        cc=query.cc,
        limit=query.limit or 100,
        offset=query.offset or 0
    )
    
    time_trials = await handle(command)
    
    response_data = []
    for time_trial in time_trials:
        response_data.append(TimeTrialResponseData(
            id=time_trial.id,
            version=time_trial.version,
            player_id=time_trial.player_id,
            game=time_trial.game,
            track=time_trial.track,
            time_ms=time_trial.time_ms,
            data=time_trial.data,
            created_at=time_trial.created_at,
            updated_at=time_trial.updated_at,
            proof_url=time_trial.proof_url,
            description=time_trial.description
        ).__dict__)
    
    return JSONResponse(response_data)


@require_permission(permissions.DELETE_TIME_TRIAL, check_denied_only=True)
async def delete_time_trial(request: Request) -> JSONResponse:
    """Delete a time trial record."""
    trial_id = request.path_params['trial_id']
    
    command = DeleteTimeTrialCommand(trial_id=trial_id)
    success = await handle(command)
    
    if success:
        return JSONResponse({'message': 'Time trial deleted successfully'})
    else:
        return JSONResponse({'error': 'Failed to delete time trial'}, status_code=400)


routes = [
    Route('/api/time-trials/create', create_time_trial, methods=['POST']),
    Route('/api/time-trials/list', list_time_trials, methods=['GET']),
    Route('/api/time-trials/{trial_id:int}', get_time_trial, methods=['GET']),
    Route('/api/time-trials/{trial_id:int}/delete', delete_time_trial, methods=['DELETE']),
]
