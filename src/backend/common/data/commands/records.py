from dataclasses import dataclass

import msgspec
from common.data.commands import Command, save_to_command_log
from common.data.models import *


@save_to_command_log
@dataclass
class SubmitRecordCommand(Command[int]):
    player_id: int
    record: Record

    async def handle(self, db_wrapper, s3_wrapper) -> int:
        async with db_wrapper.connect() as db:
            inserted_row = await db.execute_insert(
                "INSERT INTO records(player_id) VALUES (?)",
                (self.player_id, ))
            
            if inserted_row is None:
                raise Problem("Failed to create record object in DB")
            
            await db.commit()
            
        self.record.id = int(inserted_row[0])
        self.record.version = 0

        record_serialized = msgspec.json.encode(self.record)
        await s3_wrapper.put_object("records", f"{self.record.id}.json", record_serialized)
        return self.record.id

@save_to_command_log
@dataclass
class UpdateRecordCommand(Command[None]):
    record: Record

    async def handle(self, db_wrapper, s3_wrapper):
        id = self.record.id
        version = self.record.version
        async with db_wrapper.connect() as db:
            async with db.execute(
                "UPDATE records SET version = ? WHERE id = ? AND version = ?", 
                (version + 1, id, version)) as cursor:
                # TODO: run further queries to identify if the problem is that the record doesn't exist or that 
                # there were changes made
                if cursor.rowcount != 1:
                    raise Problem("Unable to update record, please try again")
            
            await db.commit()

        version += 1
        self.record.version = version

        record_serialized = msgspec.json.encode(self.record)
        await s3_wrapper.put_object("records", f"{id}_{version}.json", record_serialized)