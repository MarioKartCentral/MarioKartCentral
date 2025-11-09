import os
from common.data.db import all_dbs

def get_db_paths(db_directory: str) -> dict[str, str]:
    return {db_name: os.path.join(db_directory, f"{db_name}.db") for db_name in all_dbs}
