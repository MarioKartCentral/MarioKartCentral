from common.data.db.common import DatabaseSchema
from . import tables

schema: DatabaseSchema = DatabaseSchema(db_name='auth', tables=tables.auth_tables, indices=[])