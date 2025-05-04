from common.data.db.common import DatabaseSchema
from common.data.db.command_logs.tables import all_tables

db_name = 'command_logs'
schema = DatabaseSchema(db_name, all_tables, [])
