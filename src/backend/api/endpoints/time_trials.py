from typing import List, Dict, Any

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
    MarkProofInvalidCommand,
    MarkProofValidCommand,  # New command for MVP
    ListProofsForValidationCommand,
    EditTimeTrialPropertiesCommand,
    ListPlayerRecordsCommand,
    GetLeaderboardCommand,
    MarkTimeTrialInvalidCommand
)
from common.data.models.time_trials_api import (
    CreateTimeTrialRequestData,
    EditTimeTrialRequestData,
    TimeTrialFilter,
    TimeTrialResponseData,
    ProofResponseData, 
    ListProofsForValidationResponseData,
    PlayerRecordFilter,
    LeaderboardFilter,
)
from common.data.models import Problem


@bind_request_body(CreateTimeTrialRequestData)
# @require_permission(permissions.SUBMIT_TIME_TRIAL, check_denied_only=True)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF) # TEMPORARY
async def create_time_trial(request: Request, body: CreateTimeTrialRequestData) -> JSONResponse:
    """Create a new time trial record."""
    # Get the authenticated user from request state
    user = request.state.user
    
    # Ensure user has a linked player account
    if not user.player_id:
        raise Problem("User must have a linked player account to submit time trials", status=400)
    
    command = CreateTimeTrialCommand(
        player_id=user.player_id,  # Pass integer directly, no str() conversion
        game=body.game,
        track=body.track,
        time_ms=body.time_ms,
        proofs=body.proofs,  # Changed from proof_url
    )
    
    time_trial = await handle(command)  # Command now returns just the TimeTrial
    
    # Convert embedded proofs to ProofResponseData following established patterns
    response_proofs = [
        ProofResponseData(
            id=proof.get("id", ""),
            url=proof.get("url", ""),
            type=proof.get("type", ""),
            created_at=proof.get("created_at", ""),
            status=proof.get("status", "unvalidated"),
            validator_id=proof.get("validator_id"),
            validated_at=proof.get("validated_at"),
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
        proofs=response_proofs,  # Populate proofs with new structure
    )
    
    return JSONResponse(response_data.__dict__)


@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF) # TEMPORARY
async def get_time_trial(request: Request) -> JSONResponse:
    """Get a specific time trial by ID."""
    trial_id = request.path_params['trial_id']
    
    command = GetTimeTrialCommand(trial_id=trial_id)
    time_trial = await handle(command)  # Command returns a TimeTrial or None
    
    if time_trial is None:
        return JSONResponse({'error': 'Time trial not found'}, status_code=404)
    
    # Convert embedded proofs to ProofResponseData following established patterns
    response_proofs = [
        ProofResponseData(
            id=proof.get("id", ""),
            url=proof.get("url", ""),
            type=proof.get("type", ""),
            created_at=proof.get("created_at", ""),
            status=proof.get("status", "unvalidated"),
            validator_id=proof.get("validator_id"),
            validated_at=proof.get("validated_at"),
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
        proofs=response_proofs,  # Populate proofs with new structure
    )
    
    return JSONResponse(response_data.__dict__)


@bind_request_query(TimeTrialFilter)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF) # TEMPORARY
async def list_time_trials(request: Request, filter: TimeTrialFilter) -> JSONResponse:
    """List time trials with optional filters."""
    # Validate filter parameters using established patterns
    filter.validate()
    
    command = ListTimeTrialsCommand(
        player_id=filter.player_id,
        game=filter.game,
        track=filter.track,
        limit=filter.page_size,
        offset=(filter.page - 1) * filter.page_size
    )
    
    # Command now returns List[Tuple[TimeTrial, Optional[str], Optional[str]]]
    results_with_player_info = await handle(command)
    
    response_data_list = []
    # Unpack the tuple to include player_name and player_country_code
    for time_trial, player_name, player_country_code in results_with_player_info:
        # Create response data following established patterns
        response_data_list.append({
            "id": time_trial.id,
            "version": time_trial.version,
            "player_id": time_trial.player_id,
            "player_name": player_name,
            "player_country_code": player_country_code,
            "game": time_trial.game,
            "track": time_trial.track,
            "time_ms": time_trial.time_ms,
            "is_invalid": time_trial.is_invalid,
            "created_at": time_trial.created_at,
            "updated_at": time_trial.updated_at,
            "proofs": time_trial.proofs,  # Use raw proofs to include validations data
            "validation_status": compute_validation_status(time_trial.proofs, time_trial.is_invalid)  # Add computed validation status
        })
    
    return JSONResponse(response_data_list)


@bind_request_body(dict) 
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def mark_proof_invalid_endpoint(request: Request, body: Dict[str, Any]) -> JSONResponse:
    """
    Mark an entire proof as invalid, regardless of which properties it claims to verify.
    Requires VALIDATE_TIME_TRIAL_PROOF permission.
    """

    time_trial_id = request.path_params.get("trial_id")
    proof_id = request.path_params.get("proof_id")
    current_player_id = str(request.state.user.player_id)

    if not time_trial_id:
        raise Problem("Time Trial ID is required in path.", status=400)

    if not proof_id:
        raise Problem("Proof ID is required in path.", status=400)

    command = MarkProofInvalidCommand(
        time_trial_id=time_trial_id,
        proof_id=proof_id,
        validated_by_player_id=current_player_id,
    )
    try:
        result = await handle(command)
        return JSONResponse(result)
    except Problem as p:
        return JSONResponse(
            {"title": p.title, "detail": p.detail, "status": p.status},
            status_code=p.status,
        )
    except Exception as e:
        return JSONResponse(
            {"title": "Internal Server Error", "detail": str(e)},
            status_code=500,
        )

@bind_request_body(dict) 
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def mark_time_trial_invalid(request: Request, body: Dict[str, Any]) -> JSONResponse:
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
    )

    try:
        result = await handle(command)
        return JSONResponse(result)
    except Problem as p:
        return JSONResponse(
            {"title": p.title, "detail": p.detail, "status": p.status},
            status_code=p.status,
        )
    except Exception as e:
        return JSONResponse(
            {"title": "Internal Server Error", "detail": str(e)},
            status_code=500,
        )


@bind_request_body(dict)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def mark_proof_valid_endpoint(request: Request, body: Dict[str, Any]) -> JSONResponse:
    """
    Mark an entire proof as valid (validates both track and time for MVP).
    Requires VALIDATE_TIME_TRIAL_PROOF permission.
    """
    time_trial_id = request.path_params.get("trial_id")
    proof_id = request.path_params.get("proof_id")
    current_player_id = str(request.state.user.player_id)

    if not time_trial_id:
        raise Problem("Time Trial ID is required in path.", status=400)

    if not proof_id:
        raise Problem("Proof ID is required in path.", status=400)

    command = MarkProofValidCommand(
        proof_id=proof_id,
        validated_by_player_id=current_player_id,
        time_trial_id=time_trial_id
    )
    try:
        result = await handle(command)
        return JSONResponse(result)
    except Problem as p:
        return JSONResponse(
            {"title": p.title, "detail": p.detail, "status": p.status},
            status_code=p.status,
        )
    except Exception as e:
        return JSONResponse(
            {"title": "Internal Server Error", "detail": str(e)},
            status_code=500,
        )


@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF)
async def list_proofs_for_validation_endpoint(request: Request) -> JSONResponse:
    """
    List all proofs requiring validation, along with the status of their properties.
    Requires VALIDATE_TIME_TRIAL_PROOF permission.
    """
    command = ListProofsForValidationCommand()
    try:
        result: ListProofsForValidationResponseData = await handle(command)
        return JSONResponse(result.__dict__)
    except Problem as p:
        return JSONResponse(
            {"title": p.title, "detail": p.detail, "status": p.status},
            status_code=p.status,
        )
    except Exception as e:
        return JSONResponse(
            {"title": "Internal Server Error", "detail": str(e)},
            status_code=500,
        )


# @bind_request_body(EditTimeTrialRequestData)
# @require_permission(permissions.SUBMIT_TIME_TRIAL, check_denied_only=True)
# @require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF) # TEMPORARY
# async def edit_time_trial(request: Request, body: EditTimeTrialRequestData) -> JSONResponse:
#     """
#     Edit a time trial's properties.
    
#     Allows editing track, time_ms, and data properties. Users can edit their own time trials,
#     or staff with VALIDATE_TIME_TRIAL_PROOF permission can edit any time trial.
#     When properties are edited, validation status for those properties is reset.
#     """
#     trial_id = request.path_params['trial_id']
#     user = request.state.user
    
#     # First get the time trial to check ownership
#     get_command = GetTimeTrialCommand(trial_id=trial_id)
#     time_trial = await handle(get_command)
    
#     if time_trial is None:
#         return JSONResponse({'error': 'Time trial not found'}, status_code=404)
    
#     # Check permissions: user owns the time trial OR has validation permission
#     from common.data.commands.auth import CheckUserHasPermissionCommand
#     is_owner = time_trial.player_id == str(user.id)
#     has_validation_permission = await handle(CheckUserHasPermissionCommand(user.id, permissions.VALIDATE_TIME_TRIAL_PROOF))
    
#     if not is_owner and not has_validation_permission:
#         return JSONResponse({'error': 'You can only edit your own time trials'}, status_code=403)
    
#     # Execute the edit command
#     command = EditTimeTrialPropertiesCommand(
#         time_trial_id=trial_id,
#         user_id=str(user.id),
#         track=body.track,
#         time_ms=body.time_ms,
#     )
    
#     try:
#         result = await handle(command)
#         return JSONResponse({
#             'message': 'Time trial updated successfully',
#             'time_trial': {
#                 'id': result['id'],
#                 'track': result['track'],
#                 'time_ms': result['time_ms'],
#                 'updated_at': result['updated_at']
#             }
#         })
#     except Problem as e:
#         return JSONResponse({'error': e.detail}, status_code=e.status)


@bind_request_query(PlayerRecordFilter)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF) # TEMPORARY
async def list_player_records(request: Request, filter: PlayerRecordFilter) -> JSONResponse:
    """
    List time trial records for a specific player.
    
    Supports filtering by game/track, sorting, and pagination.
    This is a public endpoint that works without authentication.
    """
    requested_player_id = request.path_params['player_id']
    
    # Update filter with player_id from path
    filter.player_id = requested_player_id
    
    # Validate filter parameters
    try:
        filter.validate()
    except Problem as e:
        return JSONResponse({'error': e.detail}, status_code=e.status)
    
    # Execute the command
    command = ListPlayerRecordsCommand(
        player_id=requested_player_id,  # Use requested_player_id directly
        game=filter.game,
        track=filter.track,
        show_superseded=filter.show_superseded,
        sort_by=filter.sort_by,
        sort_order=filter.sort_order,
        page=filter.page,
        page_size=filter.page_size
    )
    
    try:
        result = await handle(command)
        return JSONResponse({
            'records': [
                {
                    'id': record.id,
                    'version': record.version,
                    'player_id': record.player_id,  # Added missing player_id field
                    'game': record.game,
                    'track': record.track,
                    'time_ms': record.time_ms,
                    'proofs': [
                        {
                            'id': proof.id,
                            'url': proof.url,
                            'type': proof.type,
                            'created_at': proof.created_at
                        } for proof in record.proofs
                    ],
                    'created_at': record.created_at,
                    'updated_at': record.updated_at,
                    'player_name': record.player_name,  # Added missing player_name field
                    'country_code': record.country_code,  # Added missing country_code field
                    'is_superseded': record.is_superseded,
                    'superseded_by': record.superseded_by,
                    'is_current_best': record.is_current_best,
                    'validation_status': record.validation_status
                } for record in result.records
            ],
            'total_count': result.total_count,
            'page': result.page,
            'page_size': result.page_size,
            'has_next_page': result.has_next_page
        })
    except Problem as e:
        return JSONResponse({'error': e.detail}, status_code=e.status)


@bind_request_query(LeaderboardFilter)
@require_permission(permissions.VALIDATE_TIME_TRIAL_PROOF) # TEMPORARY
async def get_leaderboard(request: Request, filter: LeaderboardFilter) -> JSONResponse:
    """Get leaderboard showing only each player's best time for tracks."""
    # Validate filter parameters
    filter.validate()
    
    # Get game from query params or use provided one
    game = filter.game if filter.game else request.query_params.get('game')
    if not game:
        return JSONResponse({'error': 'Game parameter is required'}, status_code=400)
    
    command = GetLeaderboardCommand(
        game=game,
        track=filter.track,
        include_unvalidated=filter.include_unvalidated,
        include_proofless=filter.include_proofless,
        limit=filter.page_size,
        offset=(filter.page - 1) * filter.page_size
    )
    
    try:
        records = await handle(command)
        return JSONResponse({
            'records': [
                {
                    'id': record.id,
                    'version': record.version,
                    'player_id': record.player_id,  # Added missing player_id field
                    "player_name": record.player_name,
                    "player_country_code": record.country_code,
                    'game': record.game,
                    'track': record.track,
                    'time_ms': record.time_ms,
                    'proofs': [
                        {
                            'id': proof.id,
                            'url': proof.url,
                            'type': proof.type,
                            'created_at': proof.created_at
                        } for proof in record.proofs
                    ],
                    'created_at': record.created_at,
                    'updated_at': record.updated_at,
                    'player_name': record.player_name,  # Added missing player_name field
                    'country_code': record.country_code,  # Added missing country_code field
                    'is_superseded': record.is_superseded,
                    'superseded_by': record.superseded_by,
                    'is_current_best': record.is_current_best,
                    'validation_status': record.validation_status
                } for record in records
            ],
            'page': filter.page,
            'page_size': filter.page_size,
        })
    except Problem as e:
        return JSONResponse({'error': e.detail}, status_code=e.status)


def compute_validation_status(proofs: List[Dict[str, Any]], is_invalid: bool = False) -> str:
    """
    Compute validation status based on simplified model:
    
    Record status priority:
    1. If record is marked invalid -> "invalid" 
    2. If any proof is "valid" (has any successful validations) -> "valid"
    3. If has "unvalidated" proofs (but no valid proofs) -> "unvalidated"  
    4. If no proofs OR all proofs are "invalid" -> "proofless"
    
    Simplified proof status:
    - "valid": Has ANY validation marked is_valid=True (time/track validation is implicit)
    - "invalid": Has ANY validation marked is_valid=False 
    - "unvalidated": No validations yet
    
    Note: time/track validation is now implicit when proof is marked valid.
    """
    # First check if the record itself is marked invalid
    if is_invalid:
        return "invalid"
        
    if not proofs:
        return "proofless"
    
    has_valid_proof = False
    has_unvalidated_proof = False
    
    for proof in proofs:
        # Check if this proof is marked invalid or has valid validations
        validations = proof.get("validations", {})
        is_proof_invalid = False
        has_any_valid_validations = False
        
        if validations:
            for _, validation_info in validations.items():
                if isinstance(validation_info, dict):
                    is_valid = validation_info.get("is_valid")
                    if is_valid == False:
                        is_proof_invalid = True
                        break
                    elif is_valid == True:
                        has_any_valid_validations = True
        
        # If proof is invalid, skip it (treat as if it doesn't exist)
        if is_proof_invalid:
            continue
            
        # If proof has any valid validations, it's considered a valid proof
        # (time/track validation is implicit when proof is marked valid)
        if has_any_valid_validations:
            has_valid_proof = True
        else:
            # Proof has no validations yet = unvalidated
            has_unvalidated_proof = True
    
    # Determine record status based on proof statuses
    if has_valid_proof:
        return "valid"
    elif has_unvalidated_proof:
        return "unvalidated"
    else:
        # No valid proofs and no unvalidated proofs = all proofs are invalid or no proofs
        return "proofless"


routes = [
    Route('/api/time-trials/create', create_time_trial, methods=['POST']),
    # Route('/api/time-trials/list', list_time_trials, methods=['GET']),
    Route('/api/time-trials/leaderboard', get_leaderboard, methods=['GET']),  # New leaderboard endpoint
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
    # Route('/api/time-trials/{trial_id:str}/edit', edit_time_trial, methods=['POST']),  # New edit endpoint
    Route('/api/time-trials/player/{player_id:str}/records', list_player_records, methods=['GET']),  # New player records endpoint
    Route(
        "/api/time-trials/{trial_id:str}/mark-invalid",  # New endpoint for marking entire time trial record as invalid
        mark_time_trial_invalid,
        methods=["POST"],
    ),
]
