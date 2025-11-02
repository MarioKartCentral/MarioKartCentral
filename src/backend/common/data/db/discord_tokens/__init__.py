from common.data.db.common import DatabaseSchema
from common.data.db.discord_tokens import tables, indices

schema: DatabaseSchema = DatabaseSchema(db_name='discord_tokens', tables=tables.all_tables, indices=indices.all_indices)
