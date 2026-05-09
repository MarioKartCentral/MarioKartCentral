from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import AsyncIterator, Awaitable, Callable
from aiobotocore.session import get_session
from aiomoto import mock_aws
import pytest
import pytest_asyncio
from starlette.applications import Starlette
from starlette.config import environ
from starlette.testclient import TestClient
from tests.integration.types import UserClientFactory
from tests.mocks import MockEmailService, MockIPService, MockDiscordService

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_ADMIN_EMAIL = "ADMIN@TEST.EMAIL"
TEST_ADMIN_PASSWORD = "ADMIN_PASSWORD"
TEST_USER_EMAIL = "USER@TEST.EMAIL"
TEST_USER_PASSWORD = "USER_PASSWORD"
TEST_SITE_URL = "https://testserver"
TEST_MKC_EMAIL_ADDRESS = "MKC@TEST.EMAIL"
TEST_S3_ACCESS_KEY = "TEST-S3-ACCESS-KEY"
TEST_S3_SECRET_KEY = "TEST-S3-SECRET-KEY"
TEST_S3_ENDPOINT = ""
TEST_S3_REGION = "us-east-1"
TEST_DISCORD_CLIENT_ID = "TEST-DISCORD-CLIENT-ID"
TEST_DISCORD_CLIENT_SECRET = "TEST-DISCORD-CLIENT-SECRET"
TEST_DISCORD_OAUTH_CALLBACK = ""

environ["DB_DIRECTORY"] = str(BASE_DIR / "data")
environ["S3_ACCESS_KEY"] = TEST_S3_ACCESS_KEY
environ["S3_SECRET_KEY"] = TEST_S3_SECRET_KEY
environ["S3_ENDPOINT"] = TEST_S3_ENDPOINT
environ["S3_REGION"] = TEST_S3_REGION
environ["API_ADMIN_EMAIL"] = TEST_ADMIN_EMAIL
environ["API_ADMIN_PASSWORD"] = TEST_ADMIN_PASSWORD
environ["DISCORD_CLIENT_ID"] = TEST_DISCORD_CLIENT_ID
environ["DISCORD_CLIENT_SECRET"] = TEST_DISCORD_CLIENT_SECRET
environ["DISCORD_OAUTH_CALLBACK"] = ""
environ["ENABLE_IP_LOGGING"] = "False"
environ["MKC_EMAIL_ADDRESS"] = TEST_MKC_EMAIL_ADDRESS
environ["MKC_EMAIL_HOSTNAME"] = "TEST_HOSTNAME"
environ["MKC_EMAIL_PORT"] = "1025"
environ["SITE_URL"] = TEST_SITE_URL
environ["ENV"] = "TESTING"

# app imports must be imported after setting environment variables to avoid config errors
# https://starlette.dev/config/
from api.app import app
from api.data import StateDict
from common.auth import pw_hasher
from common.auth.roles import id_by_default_role
from common.data.command_handler import CommandHandler
from common.data.commands import (
  CreateUserCommand, InitializeS3BucketsCommand, ResetDbCommand,
  ResetDuckDbCommand, SeedDatabasesCommand, SetupDuckDBSchemaCommand,
  UpdateDbSchemaCommand
)
from common.data.s3 import S3WrapperManager
from common.data.db import DBWrapper
from common.data.db.utils import get_db_paths
from common.data.duckdb.wrapper import DuckDBWrapper, DuckDBInitialiser


@pytest.fixture
def tmp_dir(tmp_path: Path):
   d = tmp_path / "data"
   logging.info(f"Making directory at path {str(d)}")
   d.mkdir(parents=True, exist_ok=True)
   yield d


@pytest.fixture
def db_paths(tmp_dir: Path):
  paths = get_db_paths(str(tmp_dir))
  logging.info(f"Creating test databases {', '.join(paths.keys())}")
  for path in paths.values():
    p = Path(path)
    p.touch(exist_ok=True)
  return paths


@pytest_asyncio.fixture
async def test_db(db_paths: dict[str, str]):
  """Sets up DB for each test"""
  logging.info("Establishing database")
  db = DBWrapper(db_paths)
  logging.info("Updating DB Schema")
  await UpdateDbSchemaCommand().handle(db)
  logging.info("Seeding database")
  await SeedDatabasesCommand(TEST_ADMIN_EMAIL, pw_hasher.hash(TEST_ADMIN_PASSWORD)).handle(db)
  yield db
  for db_name in db_paths.keys():
      await ResetDbCommand(db_name=db_name).handle(db)


@pytest_asyncio.fixture
async def test_duckdb(tmp_dir: Path):
  """Sets up DuckDB for each test"""
  logging.info("Establishing and seeding DuckDB")
  duckdb = DuckDBInitialiser.get_duckdb_wrapper(str(tmp_dir))
  await SetupDuckDBSchemaCommand().handle(duckdb)
  yield duckdb
  await ResetDuckDbCommand().handle(duckdb)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def mocked_s3_manager():
   logging.info("Creating mocked S3 wrapper manager")
   with mock_aws():
      test_session = get_session()
      yield S3WrapperManager(
          TEST_S3_SECRET_KEY,
          TEST_S3_ACCESS_KEY,
          "us-east-1",  # us-east-1 is required for mocking
          None,
          test_session
      )


@pytest_asyncio.fixture()
async def test_command_handler(test_db: DBWrapper, test_duckdb: DuckDBWrapper, mocked_s3_manager: S3WrapperManager):
    logging.info("Creating command handler with mocked dependencies")
    return CommandHandler(
        test_db,
        test_duckdb,
        mocked_s3_manager,
        MockDiscordService(TEST_DISCORD_CLIENT_ID,
                           TEST_DISCORD_CLIENT_SECRET, None),
        MockIPService(),
        MockEmailService(
            from_email=TEST_MKC_EMAIL_ADDRESS,
            site_url=TEST_SITE_URL
        )
    )


def get_test_lifespan(
    test_command_handler: CommandHandler,
):
    @asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[StateDict]:
        async with test_command_handler as handler:
            await handler.handle(InitializeS3BucketsCommand())
            yield {
                "command_handler": handler,
                "user": None,
                "session_id": None,
                "ip_address": None,
                "is_privileged": False
            }
    return lifespan


@pytest.fixture()
def create_user(test_db: DBWrapper):
    async def _create(role_name: str | None):
        user = await CreateUserCommand(TEST_USER_EMAIL, pw_hasher.hash(TEST_USER_PASSWORD)).handle(test_db)
        if role_name:
            async with test_db.connect() as db:
                query = "INSERT INTO user_roles(user_id, role_id) VALUES (?, ?)"
                await db.execute(query, (user.id, id_by_default_role[role_name]))
                await db.commit()
    return _create


@pytest.fixture()
def client(test_command_handler: CommandHandler):
    app.router.lifespan_context = get_test_lifespan(test_command_handler)
    with TestClient(app=app, base_url=TEST_SITE_URL, client=("0.0.0.0", 50000)) as client:
        yield client


@pytest_asyncio.fixture()
async def user_client_factory(client: TestClient, create_user: Callable[[str | None], Awaitable[None]]) -> UserClientFactory:
    async def _make_client(role_name: str | None):
        await create_user(role_name)
        response = client.post(
            "/api/user/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "fingerprint": {
                    "hash": "user",
                    "data": {}
                }
            }
        )
        assert response.status_code == 200
        return client
    return _make_client
