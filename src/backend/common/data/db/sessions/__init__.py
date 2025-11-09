from common.data.db.common import DatabaseSchema
from common.data.db.sessions import tables, indices

schema: DatabaseSchema = DatabaseSchema(db_name='sessions', tables=tables.all_tables, indices=indices.all_indices)