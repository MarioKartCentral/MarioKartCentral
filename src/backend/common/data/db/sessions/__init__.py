from common.data.db.common import DatabaseSchema
from . import tables
from . import indices

schema: DatabaseSchema = DatabaseSchema(db_name='sessions', tables=tables.all_tables, indices=indices.all_indices)