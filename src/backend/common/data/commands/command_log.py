from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

import msgspec

from common.data.commands import Command, get_command_log_type
from common.data.models import CommandLog, Problem, HistoricalCommandLogIndexEntry

COMMAND_LOGS_PER_FILE = 1000

@dataclass
class SaveToCommandLogCommand(Command[None]):
    command: Command[Any]

    async def handle(self, db_wrapper, s3_wrapper):
        command_name = type(self.command).__name__
        command_serialized = msgspec.json.encode(self.command).decode("utf-8")

        async with db_wrapper.connect() as db:
            await db.execute_insert(
                "INSERT INTO command_log(type, data) VALUES (?, ?)", 
                (command_name, command_serialized))
            await db.commit()

@dataclass
class GetCommandLogsCommand(Command[List[CommandLog[Command[Any]]]]):
    after_id: int | None = None

    async def handle(self, db_wrapper, s3_wrapper):
        after_id = self.after_id
        if after_id is None:
            after_id = 0

        async with db_wrapper.connect() as db:
            rows = await db.execute_fetchall(
                "SELECT id, type, data, timestamp FROM command_log WHERE id > ? ORDER BY id ASC", 
                (after_id,))
        
        log: List[CommandLog[Command[Any]]] = []
        for row in rows:
            log_id, log_type, data, timestamp = row
            command_type = get_command_log_type(log_type)
            if command_type is None:
                raise Problem("Unsupported log type", f"Unsupported log type: {log_type}")
            
            command = msgspec.json.decode(data, type=command_type)
            log.append(CommandLog(int(log_id), str(log_type), command, int(timestamp)))

        return log
    

@dataclass
class GetHistoricalCommandLogIndexCommand(Command[List[HistoricalCommandLogIndexEntry]]):
    async def handle(self, db_wrapper, s3_wrapper) -> List[HistoricalCommandLogIndexEntry]:
        index_bytes = await s3_wrapper.get_object("commandlog", "index.json")
        if not index_bytes:
            return []
        return msgspec.json.decode(index_bytes, type=List[HistoricalCommandLogIndexEntry])
    
@dataclass
class UpdateHistoricalCommandLogIndexCommand(Command[None]):
    index: List[HistoricalCommandLogIndexEntry]
    async def handle(self, db_wrapper, s3_wrapper):
        serialised = msgspec.json.encode(self.index)
        await s3_wrapper.put_object("commandlog", "index.json", serialised)

@dataclass
class GetHistoricalCommandLogLastIdCommand(Command[int | None]):
    async def handle(self, db_wrapper, s3_wrapper):
        last_id_bytes = await s3_wrapper.get_object("commandlog", "lastid")
        if last_id_bytes is None:
            return None
        return int(last_id_bytes.decode())
    
@dataclass
class UpdateHistoricalCommandLogLastIdCommand(Command[int | None]):
    last_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        serialised = str(self.last_id).encode()
        await s3_wrapper.put_object("commandlog", "lastid", serialised)
    
@dataclass
class GetHistoricalCommandLogCommand(Command[List[CommandLog[Command[Any]]]]):
    file_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        log_bytes = await s3_wrapper.get_object("commandlog", self.file_name)
        if not log_bytes:
            raise Problem("Command log not found", f"Unable to find command log with filename {self.file_name}", status=404)
        log_decoded = msgspec.json.decode(log_bytes, type=List[CommandLog[str]])
        logs: List[CommandLog[Command[Any]]] = []
        for log in log_decoded:
            command_type = get_command_log_type(log.type)
            if command_type is None:
                raise Problem("Unsupported log type", f"Unsupported log type: {log.type}")
            command = msgspec.json.decode(log.command, type=command_type)
            logs.append(CommandLog(log.id, log.type, command, log.timestamp))
        return logs
    
@dataclass
class UpdateHistoricalCommandLogCommand(Command[None]):
    file_name: str
    commands: List[CommandLog[Command[Any]]]

    async def handle(self, db_wrapper, s3_wrapper):
        serialised = msgspec.json.encode(self.commands)
        await s3_wrapper.put_object("commandlog", self.file_name, serialised)
    
@dataclass
class SaveToHistoricalCommandLogsCommand(Command[None]):
    commands: List[CommandLog[Command[Any]]]

    async def handle(self, db_wrapper, s3_wrapper):
        if not self.commands:
            return

        index = await GetHistoricalCommandLogIndexCommand().handle(db_wrapper, s3_wrapper)
        update_index = False

        commands = sorted(self.commands, key=lambda c: c.id)
        last_id = None
        while commands:
            next_command = commands[0]
            next_command_file = next_command.id // COMMAND_LOGS_PER_FILE
            last_index_entry = None if not index else index[-1]
            if last_index_entry is None or (last_index_entry.from_id == (next_command_file - 1) * COMMAND_LOGS_PER_FILE):
                # Handle case where we need a new log file and entry
                next_command_datetime = datetime.utcfromtimestamp(next_command.timestamp)
                last_index_entry = HistoricalCommandLogIndexEntry(
                    f"{next_command_datetime.strftime('%Y-%m-%d_%H-%M-%S')}_{next_command.id}.json",
                    next_command.id,
                    next_command_datetime)
                index.append(last_index_entry)
                update_index = True
                command_log_file = []
            elif last_index_entry.from_id == next_command_file * COMMAND_LOGS_PER_FILE:
                command_log_file = await GetHistoricalCommandLogCommand(last_index_entry.file_name).handle(db_wrapper, s3_wrapper)
            else:
                raise Problem("Encountered unexpected command id", f"Command ID: {next_command.id}. Latest Index ID: {last_index_entry.from_id}")

            # Handle case where commands were already in log file
            if command_log_file and command_log_file[-1].id >= next_command.id:
                min_id = command_log_file[-1].id + 1

                # skip commands until we find the first one that appears after the min ID
                for i, command in enumerate(commands):
                    if command.id >= min_id:
                        commands = commands[i:]
                        break
                else:
                    commands = []

                # Go back to the start of the while loop to try again
                continue

            max_id = (next_command_file + 1) * COMMAND_LOGS_PER_FILE
            num_commands_to_insert = len(commands)
            for i, command in enumerate(commands):
                if command.id >= max_id:
                    num_commands_to_insert = i
                    break

            commands_to_insert = commands[:num_commands_to_insert]
            if commands_to_insert:
                last_id = commands_to_insert[-1].id

            command_log_file.extend(commands_to_insert)
            await UpdateHistoricalCommandLogCommand(last_index_entry.file_name, command_log_file).handle(db_wrapper, s3_wrapper)
            commands = commands[num_commands_to_insert:]

        if update_index:
            await UpdateHistoricalCommandLogIndexCommand(index).handle(db_wrapper, s3_wrapper)
        
        if last_id is not None:
            await UpdateHistoricalCommandLogLastIdCommand(last_id).handle(db_wrapper, s3_wrapper)

    
@dataclass
class ClearCommandLogUpToIdCommand(Command[None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.execute("DELETE FROM command_log WHERE id < ?", (id,))
            await db.commit()