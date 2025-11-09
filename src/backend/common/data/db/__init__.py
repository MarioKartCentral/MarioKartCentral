# Import and re-export the database wrapper classes
from common.data.db.db_wrapper import DBWrapper, DBWrapperConnection
__all__ = ['DBWrapper', 'DBWrapperConnection', 'all_dbs']

from common.data.db.common import DatabaseSchema
from common.data.db.main import schema as main_db
from common.data.db.sessions import schema as sessions_db
from common.data.db.auth import schema as auth_db
from common.data.db.discord_tokens import schema as discord_tokens_db
from common.data.db.user_activity import schema as user_activity_db
from common.data.db.user_activity_queue import schema as user_activity_queue_db
from common.data.db.alt_flags import schema as alt_flags_db
from common.data.db.player_notes import schema as player_notes_db

all_dbs: dict[str, DatabaseSchema] = {
    main_db.db_name: main_db,
    sessions_db.db_name: sessions_db,
    auth_db.db_name: auth_db,
    discord_tokens_db.db_name: discord_tokens_db,
    user_activity_db.db_name: user_activity_db,
    user_activity_queue_db.db_name: user_activity_queue_db,
    alt_flags_db.db_name: alt_flags_db,
    player_notes_db.db_name: player_notes_db,
}