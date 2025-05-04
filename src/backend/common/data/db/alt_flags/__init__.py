from common.data.db.common import DatabaseSchema
from common.data.db.alt_flags.tables import all_tables

db_name = 'alt_flags'
schema = DatabaseSchema(db_name, all_tables, [])
