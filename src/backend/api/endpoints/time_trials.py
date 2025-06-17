from starlette.requests import Request
from starlette.routing import Route
from api.auth import require_permission, get_user_info
from api.data import handle
from api.utils.responses import JSONResponse, bind_request_body, bind_request_query
from common.auth import permissions
from common.data.commands.auth.permissions import CheckUserHasPermissionCommand
from common.data.commands.time_trials import (
    CreateTimeTrialCommand, 
    GetTimeTrialCommand, 
    MarkProofInvalidCommand,
    MarkProofValidCommand,
    ListProofsForValidationCommand,
    GetLeaderboardCommand,
    MarkTimeTrialInvalidCommand,
    EditTimeTrialCommand,
    GetTimesheetCommand
)
from common.data.models.time_trials_api import (
    CreateTimeTrialRequestData,
    EditTimeTrialRequestData,
    MarkProofInvalidRequestData,
    MarkProofValidRequestData,
    MarkTimeTrialInvalidRequestData,
    LeaderboardResponseData,
    TimeTrialResponseData,
    ProofResponseData, 
    ListProofsForValidationResponseData,
    LeaderboardFilter,
    TimesheetFilter,
    TimesheetResponseData
)
from common.data.models import Problem


@bind_request_body(CreateTimeTrialRequestData)
@require_permission(permissions.SUBMIT_TIME_TRIAL, check_denied_only=True)
async def create_time_trial(request: Request, body: CreateTimeTrialRequestData) -> JSONResponse:
    """Create a new time trial record."""
    user = request.state.user

    if not user.player_id:
        raise Problem("User must have a linked player account to submit time trials", status=400)
    
    body_player_id = body.player_id
    
    if not body_player_id:
        body_player_id = user.player_id
    elif body_player_id != user.player_id:
        can_submit_other_player = await handle(CheckUserHasPermissionCommand(user.id, permissions.VALIDATE_TIME_TRIAL_PROOF))
        if not can_submit_other_player:
            raise Problem("You do not have permission to submit time trials for other players", status=403)
    
    command = CreateTimeTrialCommand(
        player_id=body_player_id,
        game=body.game,
        track=body.track,
        time_ms=body.time_ms,
        proofs=body.proofs,
    )
    
    time_trial = await handle(command)  # Command now returns just the TimeTrial
    
    response_proofs = [
        ProofResponseData(
            id=proof.id,
            url=proof.url,
            type=proof.type,
            created_at=proof.created_at,
            status=proof.status,
            validator_id=proof.validator_id,
            validated_at=proof.validated_at,
        )
        for proof in time_trial.proofs
    ]

    response_data = TimeTrialResponseData(
        id=time_trial.id,
        version=time_trial.version,
        player_id=time_trial.player_id,
        game=time_trial.game,
        track=time_trial.track,
        time_ms=time_trial.time_ms,
        created_at=time_trial.created_at,
        updated_at=time_trial.updated_at,
        proofs=response_proofs
    )
    
    return JSONResponse(response_data)

async def get_time_trial(request: Request) -> JSONResponse:
    """Get a specific time trial by ID."""
    trial_id = request.path_params['trial_id']
    
    command = GetTimeTrialCommand(trial_id=trial_id)
    time_trial = await handle(command)  # Command returns a TimeTrial or None
    
    if time_trial is None:
        return JSONResponse({'error': 'Time trial not found'}, status_code=404)
    
    return JSONResponse(time_trial, headers={"Cache-Control": "public, max-age=60"})


@bind_request_body(MarkProofInvalidRequestData)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def mark_proof_invalid_endpoint(request: Request, body: MarkProofInvalidRequestData) -> JSONResponse:
    """
    Mark an entire proof as invalid, regardless of which properties it claims to verify.
    Requires VALIDATE_TIME_TRIAL_PROOF permission.
    """

    time_trial_id = request.path_params.get("trial_id")
    proof_id = request.path_params.get("proof_id")
    current_player_id = request.state.user.player_id

    if not time_trial_id:
        raise Problem("Time Trial ID is required in path.", status=400)

    if not proof_id:
        raise Problem("Proof ID is required in path.", status=400)

    command = MarkProofInvalidCommand(
        time_trial_id=time_trial_id,
        proof_id=proof_id,
        validated_by_player_id=current_player_id,
        version=body.version
    )
    result = await handle(command)
    return JSONResponse(result)

@bind_request_body(MarkTimeTrialInvalidRequestData)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def mark_time_trial_invalid(request: Request, body: MarkTimeTrialInvalidRequestData) -> JSONResponse:
    """
    Mark an entire time trial as invalid.
    Requires VALIDATE_TIME_TRIAL_PROOF permission.
    """

    time_trial_id = request.path_params.get("trial_id")
    current_player_id = str(request.state.user.player_id)

    if not time_trial_id:
        raise Problem("Time Trial ID is required in path.", status=400)

    command = MarkTimeTrialInvalidCommand(
        time_trial_id=time_trial_id,
        validated_by_player_id=current_player_id,
        version=body.version
    )

    result = await handle(command)
    return JSONResponse(result)


@bind_request_body(MarkProofValidRequestData)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def mark_proof_valid_endpoint(request: Request, body: MarkProofValidRequestData) -> JSONResponse:
    """
    Mark an entire proof as valid (validates both track and time for MVP).
    Requires VALIDATE_TIME_TRIAL_PROOF permission.
    """
    time_trial_id = request.path_params.get("trial_id")
    proof_id = request.path_params.get("proof_id")
    current_player_id = request.state.user.player_id

    if not time_trial_id:
        raise Problem("Time Trial ID is required in path.", status=400)

    if not proof_id:
        raise Problem("Proof ID is required in path.", status=400)

    command = MarkProofValidCommand(
        proof_id=proof_id,
        validated_by_player_id=current_player_id,
        time_trial_id=time_trial_id,
        version=body.version
    )

    result = await handle(command)
    return JSONResponse(result)


@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def list_proofs_for_validation_endpoint(request: Request) -> JSONResponse:
    """
    List all proofs requiring validation, along with the status of their properties.
    Requires VALIDATE_TIME_TRIAL_PROOF permission.
    """
    command = ListProofsForValidationCommand()
    result: ListProofsForValidationResponseData = await handle(command)
    return JSONResponse(result)

@bind_request_query(LeaderboardFilter)
async def get_leaderboard(request: Request, filter: LeaderboardFilter) -> JSONResponse:
    """Get leaderboard showing only each player's best time for tracks."""
    
    # Get game from query params or use provided one
    game = filter.game if filter.game else request.query_params.get('game')
    if not game:
        return JSONResponse({'error': 'Game parameter is required'}, status_code=400)
    
    command = GetLeaderboardCommand(
        game=game,
        track=filter.track,
        include_unvalidated=filter.include_unvalidated,
        include_proofless=filter.include_proofless,
    )
    
    records = await handle(command)
    return JSONResponse(LeaderboardResponseData(records), headers={"Cache-Control": "public, max-age=60"})

@bind_request_body(EditTimeTrialRequestData)
@require_permission(permissions.SUBMIT_TIME_TRIAL, check_denied_only=True)
async def edit_time_trial(request: Request, body: EditTimeTrialRequestData) -> JSONResponse:
    """
    Edit an existing time trial.
    - Players can edit their own trials (time, track, proofs) but not validation status or player
    - Validators can edit everything including validation status and player
    """
    time_trial_id = request.path_params.get("trial_id")
    current_player_id = request.state.user.player_id

    if not time_trial_id:
        raise Problem("Time Trial ID is required in path.", status=400)

    # Check if user has validation permissions
    check_validate_permission = CheckUserHasPermissionCommand(
        user_id=request.state.user.id,
        permission_name=permissions.VALIDATE_TIME_TRIAL_PROOF
    )
    can_validate = await handle(check_validate_permission)

    # Convert EditProofData objects to dicts for the command
    proof_dicts = []
    for proof in body.proofs:
        proof_dict = {
            'id': proof.id,
            'url': proof.url,
            'type': proof.type,
            'deleted': proof.deleted
        }
        if proof.status is not None:
            proof_dict['status'] = proof.status
        proof_dicts.append(proof_dict)

    command = EditTimeTrialCommand(
        time_trial_id=time_trial_id,
        game=body.game,
        track=body.track,
        time_ms=body.time_ms,
        proofs=proof_dicts,
        version=body.version,
        current_player_id=current_player_id,
        player_id=body.player_id,
        is_invalid=body.is_invalid,
        can_validate=can_validate
    )

    result = await handle(command)
    return JSONResponse(result)


@bind_request_query(TimesheetFilter)
@get_user_info
async def get_timesheet(request: Request, filter: TimesheetFilter) -> JSONResponse:
    """
    Get all time trials for a specific player and game across all tracks.
    Supports filtering by validation status and showing/hiding outdated times.
    Requires authentication to determine edit permissions.
    """
    # Get current user info for edit permission checking
    current_user = request.state.user
    current_player_id = current_user.player_id if current_user else None
    
    # Check if user has validation permissions (can edit any trial)
    can_validate = False
    if current_user:
        check_validate_permission = CheckUserHasPermissionCommand(
            user_id=current_user.id,
            permission_name=permissions.VALIDATE_TIME_TRIAL_PROOF
        )
        can_validate = await handle(check_validate_permission)
    
    command = GetTimesheetCommand(filter=filter)
    records = await handle(command)
    
    # Add edit permission context to each record
    for record in records:
        # User can edit if they own the trial or have validation permissions
        record.can_edit = (
            current_player_id == record.player_id or can_validate
        )
    
    return JSONResponse(TimesheetResponseData(records), headers={"Cache-Control": "public, max-age=60"})


routes = [
    Route('/api/time-trials/create', create_time_trial, methods=['POST']),
    Route('/api/time-trials/leaderboard', get_leaderboard, methods=['GET']),
    Route('/api/time-trials/timesheet', get_timesheet, methods=['GET']),  # New timesheet endpoint
    Route('/api/time-trials/{trial_id:str}', get_time_trial, methods=['GET']), # Ensure trial_id is string
    Route(
        "/api/time-trials/{trial_id:str}/proofs/{proof_id:str}/mark-invalid", # New endpoint for marking entire proof invalid
        mark_proof_invalid_endpoint,
        methods=["POST"],
    ),
    Route(
        "/api/time-trials/{trial_id:str}/proofs/{proof_id:str}/mark-valid", # New endpoint for marking entire proof valid (MVP)
        mark_proof_valid_endpoint,
        methods=["POST"],
    ),
    Route(
        "/api/time-trials/proofs/validation-queue",
        list_proofs_for_validation_endpoint,
        methods=["GET"],
    ),
    Route(
        "/api/time-trials/{trial_id:str}/mark-invalid",  # New endpoint for marking entire time trial record as invalid
        mark_time_trial_invalid,
        methods=["POST"],
    ),
    Route(
        "/api/time-trials/{trial_id:str}/edit",  # New endpoint for editing an existing time trial
        edit_time_trial,
        methods=["POST"],
    ),
    Route(
        "/api/time-trials/timesheet",
        get_timesheet,
        methods=["GET"],
    ),
]
