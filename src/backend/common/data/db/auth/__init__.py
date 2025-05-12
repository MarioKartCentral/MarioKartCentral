from common.data.db.common import DatabaseSchema
from . import tables
from . import indices

schema: DatabaseSchema = DatabaseSchema(db_name='auth', tables=tables.auth_tables, indices=indices.all_indices)