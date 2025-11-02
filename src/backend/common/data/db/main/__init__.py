from common.data.db.common import DatabaseSchema
from common.data.db.main import tables, indices

schema: DatabaseSchema = DatabaseSchema(db_name='main', tables=tables.all_tables, indices=indices.all_indices)