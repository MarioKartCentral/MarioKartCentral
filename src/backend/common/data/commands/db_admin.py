import aiosqlite
import re
from typing import Iterable
from dataclasses import dataclass
from common.auth import permissions, roles, team_permissions, team_roles, series_permissions, series_roles, tournament_permissions, tournament_roles
from common.data.commands import Command
from common.data.db.tables import all_tables
from common.data.models import Problem

class ResetDbCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        db_wrapper.reset_db()

class UpdateDbSchemaCommand(Command[None]):
    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect(autocommit=True) as db:
            await db.execute("pragma journal_mode = WAL;")
            await db.execute("pragma synchronous = NORMAL;")
        
        async with db_wrapper.connect(autocommit=False) as db:
            # Create a clean DB, so that we can compare it against our current schema
            async with aiosqlite.connect(":memory:") as clean_db:
                for table in all_tables:
                    await clean_db.execute(table.get_create_table_command())

                def parse_schema_row(row: aiosqlite.Row):
                    type, name, tbl_name, sql = row
                    return str(type), str(name), str(tbl_name), str(sql)
                
                def normalise_sql(sql: str):
                    return re.sub(r"\"(\w+)\"", r"\1", sql)
                
                def get_tables_from_schema(schema_rows: Iterable[tuple[str, str, str, str]]):
                    return { name: normalise_sql(sql) for type, name, _, sql in schema_rows if type == "table" and not name.startswith("sqlite_") }
                
                def get_indices_from_schema(schema_rows: Iterable[tuple[str, str, str, str]]):
                    return { name: normalise_sql(sql) for type, name, _, sql in schema_rows if type == "index" and not name.startswith("sqlite_") }

                fetch_schema_sql = "SELECT type, name, tbl_name, sql FROM sqlite_schema"
                clean_schema = map(parse_schema_row, await clean_db.execute_fetchall(fetch_schema_sql))
                actual_schema = map(parse_schema_row, await db.execute_fetchall(fetch_schema_sql))

                clean_tables = get_tables_from_schema(clean_schema)
                actual_tables = get_tables_from_schema(actual_schema)

                modified_tables: list[str] = []
                for table, sql in clean_tables.items():
                    if (actual_sql := actual_tables.get(table)) is not None:
                        if sql != actual_sql:
                            modified_tables.append(table)
                    else:
                        # for new tables, create them
                        print(f"Creating table {table}\n{sql}")
                        await db.execute(sql)
                
                for table in actual_tables:
                    if table not in clean_tables:
                        print(f"Table '{table}' has been removed. The table will be kept, but should be deleted manually later once the data has been preserved.")
                
                # update any tables that were modified
                for table in modified_tables:
                    print(f"Detected schema change in table '{table}'")
                    fetch_table_schema_sql = f"SELECT name FROM pragma_table_info(\'{table}\')"
                    clean_columns = [str(row[0]) for row in await clean_db.execute_fetchall(fetch_table_schema_sql)]
                    actual_columns = [str(row[0]) for row in await db.execute_fetchall(fetch_table_schema_sql)]

                    existing_columns: list[str] = []
                    for column in actual_columns:
                        if column in clean_columns:
                            existing_columns.append(column) 
                        else:
                            raise Problem(f"Unable to apply migration because column '{column}' is removed from table '{table}'")
                        
                    for column in clean_columns:
                        if column not in actual_columns:
                            print(f"New column '{column}' detected in table '{table}'")

                    # create a temp table
                    temp_table_name = table + "_temp"
                    create_temp_table_sql = clean_tables[table].replace(table, temp_table_name, 1)
                    print(f"Creating temp table {temp_table_name}\n{create_temp_table_sql}")
                    await db.execute(create_temp_table_sql)

                    # copy everything over
                    common_columns = ",".join(existing_columns)
                    print(f"Copying data from {table} to {temp_table_name}")
                    await db.execute(f"INSERT INTO {temp_table_name} ({common_columns}) SELECT {common_columns} FROM {table}")

                    # drop the old table
                    print(f"Deleting {table}")
                    await db.execute(f"DROP TABLE {table}")

                    # rename the temp table to the correct name
                    print(f"Renaming {temp_table_name} to {table}")
                    await db.execute(f"ALTER TABLE {temp_table_name} RENAME TO {table}")

                clean_indices = get_indices_from_schema(clean_schema)
                actual_indices = get_indices_from_schema(actual_schema)

                for index, sql in clean_indices:
                    if (actual_sql := actual_indices.get(index)) is not None:
                        # for changed indices, drop and recreate them
                        if sql != actual_sql:
                            print(f"Index '{index}' modified, dropping index")
                            await db.execute(f"DROP INDEX {index}")

                            print(f"Rereating index '{index}'\n{sql}")
                            await db.execute(sql)
                    else:
                        # for new indices, create them
                        print(f"Creating index '{index}'\n{sql}")
                        await db.execute(sql)

                for index in actual_indices:
                    if index not in clean_indices:
                        # for removed indices, drop them
                        print(f"Index '{index}' removed, dropping index")
                        await db.execute(f"DROP INDEX {index}")

                await db.execute("PRAGMA foreign_key_check")

                await db.commit()
            

@dataclass
class SeedDatabaseCommand(Command[None]):
    admin_email: str
    hashed_pw: str

    async def handle(self, db_wrapper, s3_wrapper):
        async with db_wrapper.connect() as db:
            await db.executemany(
                "INSERT INTO roles(id, name, position) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                roles.default_roles)
            
            await db.executemany(
                "INSERT INTO permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                permissions.permissions_by_id.items())
            
            await db.executemany(
                "INSERT INTO role_permissions(role_id, permission_id, is_denied) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                roles.default_role_permission_ids)

            await db.executemany(
                "INSERT INTO team_roles(id, name, position) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                team_roles.default_roles)
            
            await db.executemany(
                "INSERT INTO team_permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                team_permissions.permissions_by_id.items())
            
            await db.executemany(
                "INSERT INTO team_role_permissions(role_id, permission_id, is_denied) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                team_roles.default_role_permission_ids)
            
            await db.executemany(
                "INSERT INTO series_roles(id, name, position) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                series_roles.default_roles)
            
            await db.executemany(
                "INSERT INTO series_permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                series_permissions.permissions_by_id.items())
            
            await db.executemany(
                "INSERT INTO series_role_permissions(role_id, permission_id, is_denied) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                series_roles.default_role_permission_ids)
            
            await db.executemany(
                "INSERT INTO tournament_roles(id, name, position) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                tournament_roles.default_roles)

            await db.executemany(
                "INSERT INTO tournament_permissions(id, name) VALUES (?, ?) ON CONFLICT DO NOTHING",
                tournament_permissions.permissions_by_id.items())

            await db.executemany(
                "INSERT INTO tournament_role_permissions(role_id, permission_id, is_denied) VALUES(?, ?, ?) ON CONFLICT DO NOTHING",
                tournament_roles.default_role_permission_ids)
            
            await db.execute("INSERT INTO users(id, email, password_hash) VALUES (0, ?, ?)  ON CONFLICT DO NOTHING", (self.admin_email, self.hashed_pw))
            await db.execute("INSERT INTO user_roles(user_id, role_id) VALUES (0, 0) ON CONFLICT DO NOTHING")
            await db.execute("INSERT INTO user_settings(user_id) VALUES (0) ON CONFLICT DO NOTHING")
            await db.commit()