from collections import defaultdict
from dataclasses import dataclass

import base64
import hashlib
import msgspec
from common.data.commands import Command, save_to_command_log
from common.data.commands.command_log import GetCommandLogsCommand, GetLatestCommandLogIdCommand
from common.data.commands.players import UpdatePlayerCommand
from common.data.db import DBWrapper
from common.data.models import *

def _get_record_file_name(id: int, version: int):
    file_name_suffix = "" if version == 0 else f"_{version}"
    return f"{id}{file_name_suffix}.json"

@dataclass
class GetRecordData(Command[RecordMetadata]):
    record_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT player_id, version FROM records WHERE id = ?", (self.record_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Unable to find record with given ID")
                player_id, version = row
        file_name = _get_record_file_name(self.record_id, version)
        # TODO: make the file name a URL
        return RecordMetadata(self.record_id, version, player_id, file_name)

@dataclass
class UpdateRecordDataInS3(Command[None]):
    record: Record

    async def handle(self, db_wrapper, s3_wrapper):
        file_name = _get_record_file_name(self.record.id, self.record.version)
        record_serialized = msgspec.json.encode(self.record)
        await s3_wrapper.put_object("records", file_name, record_serialized)

@dataclass
class GetRecordDataFromS3(Command[Record]):
    id: int
    version: int

    async def handle(self, db_wrapper, s3_wrapper):
        file_name = _get_record_file_name(self.id, self.version)
        record_bytes = await s3_wrapper.get_object("records", file_name)
        if record_bytes is None:
            raise Problem("Unable to find record data with given ID", status=404)
        return msgspec.json.decode(record_bytes, type=Record)

@dataclass
class GetRecordCacheUpdates(Command[RecordCacheUpdates]):
    after_id: int | None
    async def handle(self, db_wrapper, s3_wrapper) -> RecordCacheUpdates:
        command_log = await GetCommandLogsCommand(self.after_id).handle(db_wrapper, s3_wrapper)
        return GetRecordCacheUpdates.get_updates_from_log(command_log)

    @staticmethod
    def get_updates_from_log(command_log: list[CommandLog[Command[Any]]]):
        records: list[Record] = []
        players: list[RecordPlayerData] = []
        for command in command_log:
            if isinstance(command, SubmitRecordCommand) or isinstance(command, UpdateRecordCommand):
                records.append(command.record)
            if isinstance(command, UpdatePlayerCommand):
                edit_player_data = command.data
                players.append(RecordPlayerData(edit_player_data.player_id, edit_player_data.name, edit_player_data.country_code))
        return RecordCacheUpdates(records, players)

@save_to_command_log
@dataclass
class SubmitRecordCommand(Command[int]):
    record: Record

    async def handle(self, db_wrapper, s3_wrapper) -> int:
        async with db_wrapper.connect() as db:
            inserted_row = await db.execute_insert(
                "INSERT INTO records(player_id) VALUES (?)",
                (self.record.player_id, ))

            if inserted_row is None:
                raise Problem("Failed to create record object in DB")

            await db.commit()

        self.record.id = int(inserted_row[0])
        self.record.version = 0

        await UpdateRecordDataInS3(self.record).handle(db_wrapper, s3_wrapper)

        return self.record.id

@save_to_command_log
@dataclass
class UpdateRecordCommand(Command[None]):
    record: Record

    async def handle(self, db_wrapper, s3_wrapper):
        id = self.record.id
        version = self.record.version

        prev_record = await GetRecordDataFromS3(id, version).handle(db_wrapper, s3_wrapper)
        if prev_record.game != self.record.game or prev_record.type != self.record.type or \
            prev_record.cc != self.record.cc or prev_record.course != self.record.course or \
            prev_record.player_id != self.record.player_id:
            raise Problem("Failed to update record", detail="Update changes a property that can't be changed", status=400)

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

        await UpdateRecordDataInS3(self.record).handle(db_wrapper, s3_wrapper)

@dataclass
class GetRecordCacheLatestUpdateId(Command[int | None]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT id from record_cache_latest_update_id") as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                return int(row[0])

@dataclass
class UpdateRecordCacheLatestUpdateId(Command[int | None]):
    latest_update_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            async with db.execute("UPDATE record_cache_latest_update_id SET id = ?", (self.latest_update_id,)) as cursor:
                if cursor.rowcount > 0:
                    return
            
            # In the case that there is no update id, insert it
            await db.execute(
                "INSERT INTO record_cache_latest_update_id(id) VALUES (?) WHERE NOT EXISTS(SELECT 1 FROM record_cache_latest_update_id)",
                (self.latest_update_id,))

@dataclass
class GetRecordCacheFileNameForCategory(Command[str | None]):
    category: RecordCategory

    async def handle(self, db_wrapper, s3_wrapper):
        query = "SELECT file_name FROM category_record_caches WHERE game = ? and type = ? and cc = ? and course = ?"
        variable_parameters = (self.category.game, self.category.type, self.category.cc, self.category.course)

        async with db_wrapper.connect() as db:
            async with db.execute(query, variable_parameters) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                return str(row[0])
@dataclass
class UpdateRecordCacheFileNameForCategory(Command[None]):
    category: RecordCategory
    file_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        # upsert in a single query
        query = """INSERT INTO category_record_caches(game, type, cc, course, file_name) 
            VALUES (?, ?, ?, ?, ?) 
            ON CONFLICT(game, type, cc, course)
            DO UPDATE SET file_name = ?"""
        variable_parameters = (self.category.game, self.category.type, self.category.cc, self.category.course, self.file_name, self.file_name)

        async with db_wrapper.connect() as db:
            async with db.execute(query, variable_parameters) as cursor:
                rowcount = cursor.rowcount
        
        if rowcount == 0:
            raise Problem("Failed to update record cache DB info")

@dataclass
class UpdateRecordCacheForCategory(Command[None]):
    cache: CategoryRecordCache

    async def handle(self, db_wrapper, s3_wrapper):
        cache_serialized = msgspec.json.encode(self.cache)
        hash_bytes = hashlib.sha256(cache_serialized).digest()
        hash_str = base64.b32encode(hash_bytes).decode()
        category = self.cache.category
        segments = ["category", category.game, category.type, category.cc, category.course]
        segments = [s for s in segments if s != "None"]
        file_name = f"{"/".join(segments)}/{hash_str}.json"
        await s3_wrapper.put_object("records", file_name, cache_serialized)
        await UpdateRecordCacheFileNameForCategory(self.cache.category, file_name).handle(db_wrapper, s3_wrapper)

@dataclass
class GetRecordsForCategory(Command[CategoryRecordListMetadata]):
    category: RecordCategory

    async def handle(self, db_wrapper, s3_wrapper):
        last_update_id = await GetRecordCacheLatestUpdateId().handle(db_wrapper, s3_wrapper)
        file_name = await GetRecordCacheFileNameForCategory(self.category).handle(db_wrapper, s3_wrapper)
        updates = await GetRecordCacheUpdates(last_update_id).handle(db_wrapper, s3_wrapper)
        updated_records = [
            r for r in updates.records 
            if r.game == self.category.game and r.type == self.category.type and
               str(r.cc) == self.category.cc and str(r.course) == self.category.course ]
        # TODO: make the file name a URL
        return CategoryRecordListMetadata(file_name, updates.players, updated_records)

@dataclass
class GetRecordCacheFileNameForPlayer(Command[str | None]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        query = "SELECT file_name FROM player_record_caches WHERE player_id = ?"
        variable_parameters = (self.player_id,)
        async with db_wrapper.connect() as db:
            async with db.execute(query, variable_parameters) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                return str(row[0])

async def _get_player_record_data(player_id: int, db_wrapper: DBWrapper):
    async with db_wrapper.connect() as db:
        async with db.execute("SELECT name, country FROM players WHERE id = ?", (player_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                raise Problem("Unable to find player with given id")
            return RecordPlayerData(player_id, str(row[0]), str(row[1]))

@dataclass
class UpdateRecordCacheFileNameForPlayer(Command[None]):
    player_id: int
    file_name: str

    async def handle(self, db_wrapper, s3_wrapper):
        # upsert in a single query
        query = """INSERT INTO player_record_caches(player_id, file_name) 
            VALUES (?, ?) 
            ON CONFLICT(player_id)
            DO UPDATE SET file_name = ?"""
        variable_parameters = (self.player_id, self.file_name, self.file_name)

        async with db_wrapper.connect() as db:
            async with db.execute(query, variable_parameters) as cursor:
                rowcount = cursor.rowcount
        
        if rowcount == 0:
            raise Problem("Failed to update record cache DB info")

@dataclass
class UpdateRecordCacheForPlayer(Command[None]):
    cache: PlayerRecordCache

    async def handle(self, db_wrapper, s3_wrapper):
        cache_serialized = msgspec.json.encode(self.cache)
        hash_bytes = hashlib.sha256(cache_serialized).digest()
        hash_str = base64.b32encode(hash_bytes).decode()
        file_name = f"player/{self.cache.player.id}/{hash_str}.json"
        await s3_wrapper.put_object("records", file_name, cache_serialized)
        await UpdateRecordCacheFileNameForPlayer(self.cache.player.id, file_name).handle(db_wrapper, s3_wrapper)

@dataclass
class GetRecordsForPlayer(Command[PlayerRecordListMetadata]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        last_update_id = await GetRecordCacheLatestUpdateId().handle(db_wrapper, s3_wrapper)
        file_name = await GetRecordCacheFileNameForPlayer(self.player_id).handle(db_wrapper, s3_wrapper)
        updates = await GetRecordCacheUpdates(last_update_id).handle(db_wrapper, s3_wrapper)
        player_data = await _get_player_record_data(self.player_id, db_wrapper)
        updated_records = [r for r in updates.records if r.player_id == self.player_id]
        # TODO: make the file name a URL
        return PlayerRecordListMetadata(player_data, file_name, updated_records)

@dataclass
class PopulateAllRecordCaches(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        last_update_id = await GetLatestCommandLogIdCommand().handle(db_wrapper, s3_wrapper)

        player_data_lookup: dict[int, RecordPlayerData] = {}
        player_caches: dict[int, list[Record]] = {}
        category_caches: dict[RecordCategory, list[Record]] = {}
        async with db_wrapper.connect(readonly=True) as db:
            record_rows = await db.execute_fetchall(
                "SELECT r.id, r.version, p.id, p.name, p.country_code FROM records r JOIN players p on p.id = r.player_id")
            
        for record_id, record_version, player_id, player_name, player_country in record_rows:
            player_data = RecordPlayerData(int(player_id), player_name, player_country)
            record_data = await GetRecordDataFromS3(record_id, record_version).handle(db_wrapper, s3_wrapper)

            player_data_lookup[player_data.id] = player_data
            player_cache = player_caches.get(player_data.id)
            if player_cache is None:
                player_cache = player_caches[player_data.id] = []
            player_cache.append(record_data)

            category = RecordCategory(record_data.game, record_data.type, str(record_data.cc), str(record_data.course))
            category_cache = category_caches.get(category)
            if category_cache is None:
                category_cache = category_caches[category] = []
            category_cache.append(record_data)

        for player_id, records_list in player_caches.items():
            player_cache = PlayerRecordCache(player_data_lookup[player_id], records_list)
            await UpdateRecordCacheForPlayer(player_cache).handle(db_wrapper, s3_wrapper)

        for category, records_list in category_caches.items():
            player_ids = set(r.player_id for r in records_list)
            players = [player_data_lookup[player_id] for player_id in player_ids]
            category_cache = CategoryRecordCache(category, players, records_list)
            await UpdateRecordCacheForCategory(category_cache).handle(db_wrapper, s3_wrapper)

        await UpdateRecordCacheLatestUpdateId(last_update_id).handle(db_wrapper, s3_wrapper)

@dataclass
class UpdateRecordCaches(Command[None]):
    updates: RecordCacheUpdates
    async def handle(self, db_wrapper, s3_wrapper):
        player_details: dict[int, RecordPlayerData] = { p.id: p for p in self.updates.players }
        updated_records_by_player: dict[int, dict[int, Record]] = defaultdict(lambda: {})
        updated_records_by_category: dict[RecordCategory, dict[int, Record]] = defaultdict(lambda: {})
        for record in self.updates.records:
            updated_records_by_player[record.player_id][record.id] = record
            category = RecordCategory(record.game, record.type, str(record.cc), str(record.course))
            updated_records_by_category[category][record.id] = record

        categories_with_updated_players: set[RecordCategory] = set()
        player_caches_to_update = set(player_details.keys()).union(updated_records_by_player.keys())
        for player_id in player_caches_to_update:
            player_data = player_details.get(player_id)
            if player_data is None:
                async with db_wrapper.connect() as db:
                    async with db.execute("SELECT name, country FROM players WHERE id = ?", (player_id,)) as cursor:
                        row = await cursor.fetchone()
                        if row is None:
                            raise Problem("Unable to find player with given id")
                        player_data = RecordPlayerData(player_id, str(row[0]), str(row[1]))
                player_details[player_id] = player_data

            player_cache_filename = await GetRecordCacheFileNameForPlayer(player_id).handle(db_wrapper, s3_wrapper)
            if player_cache_filename is None:
                player_cache = PlayerRecordCache(player_data, [])
            else:
                player_cache_bytes = await s3_wrapper.get_object("records", player_cache_filename)
                if player_cache_bytes is None:
                    raise Problem("Player record cache is missing")
                player_cache = msgspec.json.decode(player_cache_bytes, type=PlayerRecordCache)

            player_cache.player = player_data

            for record in player_cache.records:
                categories_with_updated_players.add(RecordCategory(record.game, record.type, str(record.cc), str(record.course)))

            for record_id, updated_record in updated_records_by_player[player_id].items():
                for i, record in enumerate(player_cache.records):
                    if record.id == record_id:
                        player_cache.records[i] = updated_record
                        break
                else:
                    player_cache.records.append(updated_record)
            
            await UpdateRecordCacheForPlayer(player_cache).handle(db_wrapper, s3_wrapper)

        categories_to_update = set(updated_records_by_category.keys()).union(categories_with_updated_players)
        for category in categories_to_update:
            category_cache_filename = await GetRecordCacheFileNameForCategory(category).handle(db_wrapper, s3_wrapper)
            if category_cache_filename is None:
                category_cache = CategoryRecordCache(category, [], [])
            else:
                category_cache_bytes = await s3_wrapper.get_object("records", category_cache_filename)
                if category_cache_bytes is None:
                    raise Problem("Category record cache is missing")
                category_cache = msgspec.json.decode(category_cache_bytes, type=CategoryRecordCache)
        
            for record_id, updated_record in updated_records_by_category[category].items():
                for i, record in enumerate(category_cache.records):
                    if record.id == record_id:
                        category_cache.records[i] = updated_record
                        break
                else:
                    category_cache.records.append(updated_record)

            for record in category_cache.records:
                updated_player_data = player_details.get(record.player_id)
                if updated_player_data is None:
                    continue
                
                for i, player in enumerate(category_cache.players):
                    if player.id == record.player_id:
                        category_cache.players[i] = updated_player_data
                        break
                else:
                    category_cache.players.append(updated_player_data)

            await UpdateRecordCacheForCategory(category_cache).handle(db_wrapper, s3_wrapper)