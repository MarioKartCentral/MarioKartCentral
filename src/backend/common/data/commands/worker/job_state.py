from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar, Generic, Any, cast
import msgspec
from common.data.command import Command
from common.data.db import DBWrapper

T = TypeVar('T')

@dataclass
class GetJobStateCommand(Generic[T], Command[T | None]):
    job_name: str
    state_type: type[T] = field(default_factory=lambda: cast(type[T], str))

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name='main', readonly=True) as db:
            async with db.execute(
                "SELECT state FROM job_states WHERE job_name = :job_name",
                {"job_name": self.job_name}
            ) as cursor:
                row = await cursor.fetchone()
                
        if not row:
            return None
            
        state_str = row[0]
        if self.state_type is str:
            return cast(T, state_str)
            
        return msgspec.json.decode(state_str.encode(), type=self.state_type)


@dataclass
class UpdateJobStateCommand(Command[None]):
    job_name: str
    state: Any  # Will be serialized to JSON
    
    async def handle(self, db_wrapper: DBWrapper):
        # Convert state to JSON string
        if isinstance(self.state, str):
            # If already a string, assume it's already valid JSON
            state_json = self.state
        else:
            try:
                # Otherwise, encode to JSON using msgspec
                state_json = msgspec.json.encode(self.state).decode()
            except Exception as e:
                raise ValueError(f"Failed to serialize job state: {str(e)}")
        
        timestamp = int(datetime.now().timestamp())
        
        async with db_wrapper.connect(db_name='main') as db:
            # Use INSERT OR REPLACE to handle both new and existing states
            await db.execute(
                """
                INSERT OR REPLACE INTO job_states(job_name, state, updated_on)
                VALUES(:job_name, :state, :updated_on)
                """,
                {
                    "job_name": self.job_name,
                    "state": state_json,
                    "updated_on": timestamp
                }
            )
            await db.commit()
