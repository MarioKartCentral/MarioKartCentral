from dataclasses import dataclass
from typing import Any
from common.data.commands import Command, save_to_command_log
from common.data.models import *


@save_to_command_log
@dataclass
class CreateUserSettingsCommand(Command[None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.connect() as db:
            async with db.execute("INSERT INTO user_settings(user_id) VALUES (?)", (self.user_id,)) as cursor:
                rows_inserted = cursor.rowcount

            if rows_inserted != 1:
                raise Problem("Failed to create user settings")
            
            await db.commit()

@dataclass
class GetUserSettingsCommand(Command[UserSettings | None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(readonly=True) as db:
            async with db.execute("""SELECT avatar, about_me, language, 
                color_scheme, timezone, hide_discord FROM user_settings WHERE user_id = ?""", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
        avatar, about_me, language, color_scheme, timezone, hide_discord = row

        return UserSettings(self.user_id, avatar, about_me, language, color_scheme, timezone, bool(hide_discord))
    
@save_to_command_log
@dataclass
class EditUserSettingsCommand(Command[bool]):
    user_id: int
    data: EditUserSettingsRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        set_clauses: list[str] = []
        variable_parameters: list[Any] = []

        def set_value(value: Any, column_name: str):
            if value is not None:
                set_clauses.append(f"{column_name} = ?")
                variable_parameters.append(value)

        set_value(data.avatar, "avatar")
        set_value(data.about_me, "about_me")
        set_value(data.language, "language")
        set_value(data.color_scheme, "color_scheme")
        set_value(data.timezone, "timezone")
        set_value(data.hide_discord, "hide_discord")

        if data.about_me and len(data.about_me) > 500:
            raise Problem("About me must be 500 characters or less", status=400)

        if not set_clauses:
            raise Problem("Bad request body", detail="There are no values to set")

        async with db_wrapper.connect() as db:
            update_query = f"UPDATE user_settings SET {', '.join(set_clauses)} WHERE user_id = ?"""
            variable_parameters.append(self.user_id)
            async with db.execute(update_query, variable_parameters) as cursor:
                if cursor.rowcount != 1:
                    return False

            await db.commit()
            return True
        
@save_to_command_log
@dataclass
class EditPlayerUserSettingsCommand(Command[None]):
    data: EditPlayerUserSettingsRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            data = self.data
            if data.about_me and len(data.about_me) > 500:
                raise Problem("About me must be 500 characters or less", status=400)
            async with db.execute("SELECT id FROM users WHERE player_id = ?", (data.player_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise Problem("Player not found", status=404)
                user_id = row[0]
            
            set_clauses: list[str] = []
            variable_parameters: list[Any] = []

            def set_value(value: Any, column_name: str):
                if value is not None:
                    set_clauses.append(f"{column_name} = ?")
                    variable_parameters.append(value)

            set_value(data.avatar, "avatar")
            set_value(data.about_me, "about_me")
            set_value(data.language, "language")
            set_value(data.color_scheme, "color_scheme")
            set_value(data.timezone, "timezone")
            set_value(data.hide_discord, "hide_discord")

            if not set_clauses:
                raise Problem("Bad request body", detail="There are no values to set")

            update_query = f"UPDATE user_settings SET {', '.join(set_clauses)} WHERE user_id = ?"""
            variable_parameters.append(user_id)
            await db.execute(update_query, variable_parameters)
            await db.commit()