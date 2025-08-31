from datetime import timedelta
from typing import List
import logging
from worker.data import handle
from worker.jobs import Job
from common.data.commands import BackupDatabasesCommand, CleanupOldBackupsCommand, DbBackupState, BackupInfo 

class DatabaseBackupJob(Job):
    @property
    def name(self):
        return "Database Backup"
    
    @property
    def delay(self):
        return timedelta(minutes=60)
    
    async def run(self):
        state = await self.get_state(DbBackupState)
        if not state:
            state = DbBackupState()
        
        backup_results: List[BackupInfo] = await handle(BackupDatabasesCommand())
        
        if not backup_results:
            logging.info("Database backup run completed, but no databases were backed up.")
            return

        first_backup = backup_results[0]
        backup_set_prefix = first_backup.s3_key.split('/')[0]
        current_backup_time = first_backup.created_at
        
        state.last_backup_time = current_backup_time
        state.last_backup_id = backup_set_prefix
        
        # Note: total_backup_size_bytes is calculated during cleanup.

        await self.update_state(state)
        
        logging.info(f"Database backup completed for set: {backup_set_prefix}. {len(backup_results)} database(s) backed up.")


class DatabaseBackupCleanupJob(Job):
    @property
    def name(self):
        return "Database Backup Cleanup"
    
    @property
    def delay(self):
        return timedelta(hours=24)
    
    async def run(self):
        deleted_backup_set_prefixes: List[str] = await handle(CleanupOldBackupsCommand())
        
        if deleted_backup_set_prefixes:
            logging.info(f"Removed {len(deleted_backup_set_prefixes)} old backup sets (prefixes): {', '.join(deleted_backup_set_prefixes)}")
        else:
            logging.info("Database backup cleanup job ran. No backup sets were deleted.")


_jobs: List[Job] = []

def get_jobs():
    if not _jobs:
        _jobs.append(DatabaseBackupJob())
        _jobs.append(DatabaseBackupCleanupJob())
    return _jobs
