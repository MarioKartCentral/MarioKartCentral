from common.data.db.common import DatabaseSchema
from common.data.db.player_notes.tables import all_tables

db_name = 'player_notes'
schema = DatabaseSchema(db_name, all_tables, [])
