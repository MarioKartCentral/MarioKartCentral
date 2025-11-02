from worker.jobs.base import Job

# Import all job modules at package level to ensure commands are registered
from worker.jobs import (
    role_checker, 
    discord_refresh, 
    unban_players_checker, 
    ip_check, 
    expired_token_check,
    activity_queue_processor,
    activity_compression,
    vpn_detection,
    ip_match_detection,
    persistent_cookie_detection,
    fingerprint_match_detection,
    db_backup,
    close_tournament_registrations
)

_jobs: list[Job] = []

def get_all_jobs():
    if not _jobs:
        _jobs.extend(role_checker.get_jobs())
        _jobs.extend(discord_refresh.get_jobs())
        _jobs.extend(unban_players_checker.get_jobs())
        _jobs.extend(ip_check.get_jobs())
        _jobs.extend(expired_token_check.get_jobs())
        _jobs.extend(activity_queue_processor.get_jobs())
        _jobs.extend(activity_compression.get_jobs())
        _jobs.extend(vpn_detection.get_jobs())
        _jobs.extend(ip_match_detection.get_jobs())
        _jobs.extend(persistent_cookie_detection.get_jobs())
        _jobs.extend(fingerprint_match_detection.get_jobs())
        _jobs.extend(db_backup.get_jobs())
        _jobs.extend(close_tournament_registrations.get_jobs())
    return _jobs