from common.data.db.common import DatabaseSchema
from common.data.db.user_activity import tables, indices

schema: DatabaseSchema = DatabaseSchema(db_name='user_activity', tables=tables.all_tables, indices=indices.all_indices)
