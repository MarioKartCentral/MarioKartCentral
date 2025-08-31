from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, List, Tuple
from common.data.commands import Command
from common.data.db.db_wrapper import DBWrapper

class GranularityLevel(Enum):
    NONE = 0
    ONE_MINUTE = 1
    TEN_MINUTES = 2
    THIRTY_MINUTES = 3
    ONE_HOUR = 4
    ONE_DAY = 5

@dataclass
class CompressUserActivityTimeRangesCommand(Command[None]):
    """
    This command compresses UserIPTimeRange records based on their age.
    
    Compression rules:
    - < 10 minutes old: no compression (NONE)
    - 10-60 minutes: 1 minute windows
    - 1-6 hours: 10 minute windows
    - 6h-2d: 30 minute windows
    - 2-30 days: 1 hour windows
    - > 30 days: 1 day windows
    """
    
    def _get_compression_boundaries(self) -> List[Tuple[int, int, GranularityLevel]]:
        """
        Returns a list of (timestamp_from, timestamp_to, target_granularity) tuples
        representing the time boundaries for each compression level
        """
        now = datetime.now(timezone.utc)
        
        # Helper function to calculate timestamp for a specific time delta from now
        def ts_ago(delta: timedelta) -> int:
            return int((now - delta).timestamp())
        
        now_ts = int(now.timestamp())
        boundaries = [
            (0,                             ts_ago(timedelta(days=30)),    GranularityLevel.ONE_DAY),
            (ts_ago(timedelta(days=30)),    ts_ago(timedelta(days=2)),     GranularityLevel.ONE_HOUR),
            (ts_ago(timedelta(days=2)),     ts_ago(timedelta(hours=6)),    GranularityLevel.THIRTY_MINUTES),
            (ts_ago(timedelta(hours=6)),    ts_ago(timedelta(hours=1)),    GranularityLevel.TEN_MINUTES),
            (ts_ago(timedelta(hours=1)),    ts_ago(timedelta(minutes=10)), GranularityLevel.ONE_MINUTE),
            (ts_ago(timedelta(minutes=10)), now_ts + 1,                    GranularityLevel.NONE),
        ]
        
        return boundaries
    
    def _align_timestamp(self, timestamp: int, granularity: GranularityLevel) -> int:
        """Aligns a timestamp to the start of the appropriate window based on granularity"""
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        if granularity == GranularityLevel.NONE:
            return timestamp  # No alignment needed
            
        elif granularity == GranularityLevel.ONE_MINUTE:
            # Align to the start of a minute
            aligned = dt.replace(second=0, microsecond=0)
            return int(aligned.timestamp())
            
        elif granularity == GranularityLevel.TEN_MINUTES:
            # Align to the start of a 10-minute window
            minute = (dt.minute // 10) * 10
            aligned = dt.replace(minute=minute, second=0, microsecond=0)
            return int(aligned.timestamp())
            
        elif granularity == GranularityLevel.THIRTY_MINUTES:
            # Align to the start of a 30-minute window
            minute = (dt.minute // 30) * 30
            aligned = dt.replace(minute=minute, second=0, microsecond=0)
            return int(aligned.timestamp())
            
        elif granularity == GranularityLevel.ONE_HOUR:
            # Align to the start of an hour
            aligned = dt.replace(minute=0, second=0, microsecond=0)
            return int(aligned.timestamp())
            
        elif granularity == GranularityLevel.ONE_DAY:
            # Align to 6AM UTC
            date = dt.date()
            six_am = datetime(date.year, date.month, date.day, 6, 0, 0, tzinfo=timezone.utc)
            # If current time is before 6AM, use previous day's 6AM
            if dt.hour < 6:
                six_am = six_am - timedelta(days=1)
            return int(six_am.timestamp())
            
        return timestamp  # Default fallback
    
    async def handle(self, db_wrapper: DBWrapper):
        boundaries = self._get_compression_boundaries()
        
        async with db_wrapper.connect(db_name='user_activity') as db:
            
            for timestamp_from, timestamp_to, target_granularity in boundaries:
                if target_granularity == GranularityLevel.NONE:
                    continue

                timestamp_to = self._align_timestamp(timestamp_to, target_granularity)
                
                # Find time ranges that need to be compressed within this boundary
                get_time_ranges_to_compress = """
                    SELECT user_ip_id, date_earliest, date_latest, times
                    FROM user_ip_time_ranges
                    WHERE date_latest BETWEEN :from_ts AND :to_ts
                    AND granularity < :target_granularity
                """
                rows = await db.execute_fetchall(get_time_ranges_to_compress, {
                    "from_ts": timestamp_from,
                    "to_ts": timestamp_to,
                    "target_granularity": target_granularity.value
                })

                if not rows:
                    continue

                time_ranges_by_window: dict[tuple[int, int], list[tuple[int, int, int]]] = {}
                for row in rows:
                    user_ip_id, date_earliest, date_latest, times = row
                    window_start = self._align_timestamp(date_earliest, target_granularity)
                    key = (user_ip_id, window_start)
                    if key not in time_ranges_by_window:
                        time_ranges_by_window[key] = []
                    time_ranges_by_window[key].append((date_earliest, date_latest, times))
                
                new_ranges: list[dict[str, Any]] = []
                for (user_ip_id, _), ranges in time_ranges_by_window.items():
                    date_earliest = min(r[0] for r in ranges)
                    date_latest = max(r[1] for r in ranges)
                    times = sum(r[2] for r in ranges)
                    new_ranges.append({
                        "user_ip_id": user_ip_id,
                        "date_earliest": date_earliest,
                        "date_latest": date_latest,
                        "times": times,
                        "granularity": target_granularity.value
                    })
                
                delete_old_query = """
                    DELETE FROM user_ip_time_ranges 
                    WHERE date_latest BETWEEN :from_ts AND :to_ts
                    AND granularity < :target_granularity
                """
                await db.execute(delete_old_query, {
                    "from_ts": timestamp_from,
                    "to_ts": timestamp_to,
                    "target_granularity": target_granularity.value
                })

                insert_new_query = """
                    INSERT INTO user_ip_time_ranges (user_ip_id, date_earliest, date_latest, times, granularity)
                    VALUES (:user_ip_id, :date_earliest, :date_latest, :times, :granularity)
                """
                await db.executemany(insert_new_query, new_ranges)
                await db.commit()
