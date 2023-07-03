from dataclasses import dataclass
from common.data.commands import Command, save_to_command_log
from common.data.models import EditUserSettingsRequestData, Problem, UserSettings


@save_to_command_log
@dataclass
class CreateUserSettingsCommand(Command[None]):
    user_id: int

    async def handle(self, db_wrapper, s3_wrapper):
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
            async with db.execute("""SELECT avatar, discord_tag, about_me, language, 
                color_scheme, timezone FROM user_settings WHERE user_id = ?""", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
        avatar, discord_tag, about_me, language, color_scheme, timezone = row

        return UserSettings(self.user_id, avatar, discord_tag, about_me, language, color_scheme, timezone)
    
@save_to_command_log
@dataclass
class EditUserSettingsCommand(Command[bool]):
    user_id: int
    data: EditUserSettingsRequestData

    async def handle(self, db_wrapper, s3_wrapper):
        data = self.data
        set_clauses = []
        variable_parameters = []

        def set_value(value, column_name):
            if value is not None:
                set_clauses.append(f"{column_name} = ?")
                variable_parameters.append(value)

        set_value(data.avatar, "avatar")
        set_value(data.discord_tag, "discord_tag")
        set_value(data.about_me, "about_me")
        set_value(data.language, "language")
        set_value(data.color_scheme, "color_scheme")
        set_value(data.timezone, "timezone")

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