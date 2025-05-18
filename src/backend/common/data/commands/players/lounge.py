from dataclasses import dataclass
from common.data.commands import Command
from common.data.models.common import Problem
from typing import Optional

@dataclass
class PlayerLoungeInfo:
    id: int
    switch_fc: Optional[str]
    country_code: str

@dataclass
class GetPlayerLoungeInfoCommand(Command[PlayerLoungeInfo]):
    player_id: int

    async def handle(self, db_wrapper, s3_wrapper) -> PlayerLoungeInfo:
        async with db_wrapper.connect(readonly=True) as db:
            query = """
                SELECT 
                    p.country_code,
                    (SELECT fc FROM friend_codes 
                     WHERE player_id = :player_id AND type = 'switch' AND is_active = 1 
                     ORDER BY is_primary DESC, id ASC LIMIT 1) as switch_fc
                FROM players p
                WHERE p.id = :player_id
            """
            async with db.execute(query, {"player_id": self.player_id}) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player not found", status=404)
                
                country_code, switch_fc = row
                
            return PlayerLoungeInfo(self.player_id, switch_fc, country_code)
