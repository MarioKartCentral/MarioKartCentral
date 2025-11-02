from common.data.db.common import DatabaseSchema
from common.data.db.auth import tables, indices

schema: DatabaseSchema = DatabaseSchema(db_name='auth', tables=tables.auth_tables, indices=indices.all_indices)