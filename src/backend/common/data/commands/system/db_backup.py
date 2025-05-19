import logging
import tempfile
import asyncio
import aiosqlite
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from pathlib import Path
from common.data.commands import Command
import common.data.s3 as s3


@dataclass
class BackupInfo:
    s3_key: str      # Full S3 key, e.g., "YYYYMMDD-HHMMSS/dbname.db"
    db_name: str     # Logical name of the database, e.g., "main"
    created_at: int  # Unix timestamp of the backup set (derived from prefix)
    size_bytes: int  # Size of this specific .db file in bytes


@dataclass
class DbBackupState:
    last_backup_time: int = 0  # Last successful backup time (unix timestamp)
    last_backup_id: str = ""   # ID/name of the last backup
    total_backup_size_bytes: int = 0  # Total size of all backups in bytes


@dataclass
class BackupDatabasesCommand(Command[List[BackupInfo]]):
    """Create a backup of all database files and store it in S3, one file per DB"""
    
    async def handle(self, db_wrapper, s3_wrapper) -> List[BackupInfo]:
        now = datetime.now(timezone.utc)
        backup_timestamp = int(now.timestamp())
        backup_set_prefix = now.strftime("%Y%m%d-%H%M%S")
        
        successful_backups: List[BackupInfo] = []
        
        # Helper function to create a single snapshot
        async def _perform_snapshot_creation(
            db_name_local: str,
            original_db_path_local: str,
            temp_snapshot_db_path_local: str
        ) -> Tuple[str, str, bool, Exception | None]:
            source_conn = None
            dest_conn = None
            temp_snapshot_path = Path(temp_snapshot_db_path_local)
            try:
                # Connect to the source database (read-only for backup)
                source_conn = await aiosqlite.connect(f'file:{original_db_path_local}?mode=ro', uri=True, timeout=10.0)
                # Create a connection to the temporary database file where the backup will be stored
                dest_conn = await aiosqlite.connect(str(temp_snapshot_path), timeout=10.0)
                # Perform the online backup to create a consistent snapshot
                await source_conn.backup(dest_conn)
            except Exception as e:
                return db_name_local, str(temp_snapshot_path), False, e
            finally:
                if source_conn:
                    await source_conn.close()
                if dest_conn:
                    await dest_conn.close()
                # Set permissions immediately after creation and closing connections
                if temp_snapshot_path.exists():
                    try:
                        temp_snapshot_path.chmod(0o600)
                    except OSError as chmod_e:
                        return db_name_local, str(temp_snapshot_path), False, chmod_e
            return db_name_local, str(temp_snapshot_path), True, None

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            db_snapshot_info_list: list[tuple[str, str, str]] = [] # List of (db_name, original_db_path, temp_snapshot_db_path)
            for db_name_iter in db_wrapper.db_paths.keys():
                original_db_path_iter = db_wrapper.db_paths[db_name_iter]
                orig_path = Path(original_db_path_iter)
                if not orig_path.exists():
                    logging.info(f"Database file not found, skipping backup: {original_db_path_iter}")
                    continue
                temp_snapshot_db_path_iter = str(temp_dir_path / f"snapshot_{db_name_iter}.db")
                db_snapshot_info_list.append((db_name_iter, original_db_path_iter, temp_snapshot_db_path_iter))

            if not db_snapshot_info_list:
                return []

            # Part 1: Concurrently create all snapshots
            snapshot_creation_tasks = [
                _perform_snapshot_creation(db_name, orig_path, temp_path)
                for db_name, orig_path, temp_path in db_snapshot_info_list
            ]
            created_snapshots_results = await asyncio.gather(*snapshot_creation_tasks, return_exceptions=False) # Exceptions are returned as part of the tuple

            # Part 2: Process each created snapshot (VACUUM, upload)
            for result_tuple in created_snapshots_results:
                db_name, temp_snapshot_db_path, success, error = result_tuple
                temp_snapshot_path = Path(temp_snapshot_db_path)
                if not success:
                    logging.warning(f"Failed to create snapshot {db_name}: {str(error)}")
                    if temp_snapshot_path.exists():
                        try:
                            temp_snapshot_path.unlink()
                        except OSError as unlink_e:
                            logging.warning(f"Failed to unlink partially created/permission-failed snapshot {temp_snapshot_db_path}: {str(unlink_e)}")
                    continue

                s3_object_key = f"{backup_set_prefix}/{db_name}.db"
                dest_conn_vacuum = None
                try:
                    # Connect to the snapshot for VACUUM
                    dest_conn_vacuum = await aiosqlite.connect(str(temp_snapshot_path), timeout=10.0)
                    await dest_conn_vacuum.execute("VACUUM")
                    await dest_conn_vacuum.commit()
                    await dest_conn_vacuum.close()
                    dest_conn_vacuum = None

                    # Read the snapshot file and upload to S3
                    with temp_snapshot_path.open("rb") as f_snapshot:
                        snapshot_data = f_snapshot.read()
                        await s3_wrapper.put_object(s3.DB_BACKUP_BUCKET, s3_object_key, snapshot_data)

                    size_bytes = temp_snapshot_path.stat().st_size

                    successful_backups.append(BackupInfo(
                        s3_key=s3_object_key,
                        db_name=db_name,
                        created_at=backup_timestamp,
                        size_bytes=size_bytes
                    ))

                except Exception as e:
                    logging.warning(f"Failed to process/upload snapshot for database {db_name} (key: {s3_object_key}): {str(e)}")
                finally:
                    if dest_conn_vacuum:
                        try:
                            await dest_conn_vacuum.close()
                        except Exception as close_e:
                            logging.warning(f"Failed to close vacuum connection for {temp_snapshot_db_path}: {str(close_e)}")
                    # Ensure temporary snapshot file is removed after processing or error
                    if temp_snapshot_path.exists():
                        try:
                            temp_snapshot_path.unlink()
                        except OSError as unlink_e:
                            logging.warning(f"Failed to unlink snapshot {temp_snapshot_db_path} after processing: {str(unlink_e)}")
        return successful_backups


@dataclass
class BackupSetInfo:
    """Represents a set of database files backed up at the same time."""
    backup_set_prefix: str  # Directory-like prefix in S3 (e.g., "YYYYMMDD-HHMMSS")
    created_at: int         # Unix timestamp derived from the prefix
    total_size_bytes: int   # Sum of sizes of all .db files in this set
    s3_keys: List[str]      # List of full S3 keys for individual .db files in this set


@dataclass
class CleanupOldBackupsCommand(Command[List[str]]):
    """Remove old backup sets according to retention policy."""
    max_hourly_backup_days: int = 7
    max_backup_size_bytes: int = 1024 * 1024 * 1024 * 100  # 100 GB

    async def handle(self, db_wrapper, s3_wrapper) -> List[str]:
        s3_objects = await s3_wrapper.list_objects(s3.DB_BACKUP_BUCKET)

        # Group S3 objects by their common prefix (backup set)
        backup_sets_data: Dict[str, Dict[str, Any]] = {}
        for obj in s3_objects:
            key = obj.get('Key', '')
            size = obj.get('Size', 0)

            # Only process keys in the format "YYYYMMDD-HHMMSS/dbname.db"
            if '/' not in key or not key.endswith('.db'):
                continue

            backup_set_prefix = key.split('/')[0]

            if backup_set_prefix not in backup_sets_data:
                try:
                    # Parse timestamp from the prefix
                    dt = datetime.strptime(backup_set_prefix, "%Y%m%d-%H%M%S")
                    timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())
                    backup_sets_data[backup_set_prefix] = {
                        'created_at': timestamp,
                        'total_size_bytes': 0,
                        's3_keys': []
                    }
                except ValueError:
                    # Skip this prefix if it's not a valid timestamp format
                    continue

            backup_sets_data[backup_set_prefix]['total_size_bytes'] += size
            backup_sets_data[backup_set_prefix]['s3_keys'].append(key)

        # Convert grouped data to BackupSetInfo objects
        all_backup_sets: List[BackupSetInfo] = []
        for prefix, data in backup_sets_data.items():
            all_backup_sets.append(BackupSetInfo(
                backup_set_prefix=prefix,
                created_at=data['created_at'],
                total_size_bytes=data['total_size_bytes'],
                s3_keys=data['s3_keys']
            ))

        if not all_backup_sets:
            return []

        # Sort by creation time (oldest first for cleanup logic)
        all_backup_sets.sort(key=lambda bs: bs.created_at)

        deleted_backup_set_prefixes: List[str] = []
        now_ts = datetime.now(timezone.utc).timestamp()
        hourly_cutoff_ts = now_ts - (self.max_hourly_backup_days * 24 * 60 * 60)

        # Identify backup sets to keep based on hourly/daily retention
        backup_sets_to_keep: List[BackupSetInfo] = []
        # For backups older than hourly_cutoff_ts, keep one per day (the newest for that day)
        daily_kept_sets: Dict[str, BackupSetInfo] = {} 

        for bs in all_backup_sets:
            backup_date = datetime.fromtimestamp(bs.created_at, tz=timezone.utc)
            if bs.created_at >= hourly_cutoff_ts:
                # Keep all hourly backups within the retention period
                backup_sets_to_keep.append(bs)
            else:
                # For older backups, keep only one per day (the newest one for that day)
                day_key = backup_date.strftime("%Y-%m-%d")
                if day_key not in daily_kept_sets or bs.created_at > daily_kept_sets[day_key].created_at:
                    daily_kept_sets[day_key] = bs
        
        # Add the selected daily backups to the keep list
        backup_sets_to_keep.extend(daily_kept_sets.values())
        
        # Remove duplicates and sort by creation time
        temp_keep_dict = {bs.backup_set_prefix: bs for bs in backup_sets_to_keep}
        backup_sets_to_keep = sorted(list(temp_keep_dict.values()), key=lambda bs: bs.created_at)

        # Identify backup sets to delete
        keep_prefixes = {bs.backup_set_prefix for bs in backup_sets_to_keep}
        backup_sets_to_delete = [bs for bs in all_backup_sets if bs.backup_set_prefix not in keep_prefixes]

        for bs_to_delete in backup_sets_to_delete:
            try:
                for s3_key in bs_to_delete.s3_keys:
                    await s3_wrapper.delete_object(s3.DB_BACKUP_BUCKET, s3_key)
                deleted_backup_set_prefixes.append(bs_to_delete.backup_set_prefix)
            except Exception as e:
                logging.error(f"Error deleting files for backup set {bs_to_delete.backup_set_prefix}: {str(e)}")
        
        # Recalculate current total size of backups we intend to keep
        current_total_size = sum(bs.total_size_bytes for bs in backup_sets_to_keep)

        # Enforce total size limit: delete oldest kept backups until under limit
        # Ensure we always keep at least one backup set if possible.
        while current_total_size > self.max_backup_size_bytes and len(backup_sets_to_keep) > 1:
            oldest_kept_set = backup_sets_to_keep.pop(0) # Oldest is at the start
            try:
                for s3_key in oldest_kept_set.s3_keys:
                    await s3_wrapper.delete_object(s3.DB_BACKUP_BUCKET, s3_key)
                if oldest_kept_set.backup_set_prefix not in deleted_backup_set_prefixes:
                    deleted_backup_set_prefixes.append(oldest_kept_set.backup_set_prefix)
                current_total_size -= oldest_kept_set.total_size_bytes
            except Exception as e:
                logging.error(f"Error deleting files for backup set {oldest_kept_set.backup_set_prefix} during size enforcement: {str(e)}")

        if deleted_backup_set_prefixes:
            final_kept_size_gb = current_total_size / (1024*1024*1024)
            max_allowed_gb = self.max_backup_size_bytes / (1024*1024*1024)
            logging.info(f"Cleanup complete. Deleted backup sets: {', '.join(deleted_backup_set_prefixes)}. " +
                        f"Remaining backup size: {final_kept_size_gb:.2f} GB. Max allowed: {max_allowed_gb:.2f} GB.")

        return deleted_backup_set_prefixes
