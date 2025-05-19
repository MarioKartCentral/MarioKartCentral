from common.data.db.user_activity_queue import tables
from common.data.db.common import DatabaseSchema

schema = DatabaseSchema(
    db_name="user_activity_queue",
    tables=tables.all_tables,
    indices=[]
)
