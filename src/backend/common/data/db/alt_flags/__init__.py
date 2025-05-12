from common.data.db.common import DatabaseSchema
from common.data.db.alt_flags.tables import all_tables
from common.data.db.alt_flags.indices import all_indices

db_name = 'alt_flags'
schema = DatabaseSchema(db_name, all_tables, all_indices)
