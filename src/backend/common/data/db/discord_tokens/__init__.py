from common.data.db.common import DatabaseSchema
from . import tables

schema: DatabaseSchema = DatabaseSchema(db_name='discord_tokens', tables=tables.all_tables, indices=[])
