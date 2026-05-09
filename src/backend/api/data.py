from contextlib import asynccontextmanager
from api import appsettings
from common.auth import pw_hasher
from common.data.command_handler import CommandHandler
from common.data.commands import *
from common.data.db.utils import get_db_paths
from common.data.models.users import User
from common.emails import SESEmailService, SMTPEmailService
from common.data.db.db_wrapper import DBWrapper
from common.data.duckdb.wrapper import DuckDBInitialiser
from common.data.s3 import S3WrapperManager
from common.discord import DiscordApi
from common.ip_api import IPApi
from starlette.applications import Starlette
from starlette.datastructures import State as StarletteState


class StateDict(TypedDict):
    command_handler: CommandHandler
    user: User | None
    session_id: str | None
    ip_address: str | None
    is_privileged: bool


@dataclass
class State(StarletteState):
    command_handler: CommandHandler
    user: User | None = None
    session_id:  str | None = None
    ip_address:  str | None = None
    is_privileged: bool = False

    @property
    def to_dict(self) -> StateDict:
        return {
            "command_handler": self.command_handler,
            "user": self.user,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "is_privileged": self.is_privileged
        }


db_paths = get_db_paths(appsettings.DB_DIRECTORY)

if appsettings.USE_SES_FOR_EMAILS:
    if not appsettings.AWS_SES_ACCESS_KEY or not appsettings.AWS_SES_SECRET_KEY:
        raise Exception(
            "AWS SES access key and secret key must be set if SES is used")
    email_service = SESEmailService(
        from_email=appsettings.MKC_EMAIL_ADDRESS,
        site_url=appsettings.SITE_URL,
        access_key_id=appsettings.AWS_SES_ACCESS_KEY,
        secret_access_key=str(appsettings.AWS_SES_SECRET_KEY),
        region=appsettings.AWS_SES_REGION
    )
else:
    email_service = SMTPEmailService(
        from_email=appsettings.MKC_EMAIL_ADDRESS,
        site_url=appsettings.SITE_URL,
        hostname=appsettings.MKC_EMAIL_HOSTNAME,
        port=appsettings.MKC_EMAIL_PORT
    )


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[StateDict]:
    _command_handler = CommandHandler(
        DBWrapper(db_paths),
        DuckDBInitialiser.get_duckdb_wrapper(appsettings.DB_DIRECTORY),
        S3WrapperManager(str(appsettings.S3_SECRET_KEY), appsettings.S3_ACCESS_KEY,
                         appsettings.S3_REGION, appsettings.S3_ENDPOINT),
        DiscordApi(appsettings.DISCORD_CLIENT_ID, str(
            appsettings.DISCORD_CLIENT_SECRET), appsettings.DISCORD_OAUTH_CALLBACK),
        IPApi(),
        email_service
    )

    async with _command_handler as handler:
        # Initialize DBs
        if appsettings.RESET_DATABASE:
            for db_name in db_paths.keys():
                await handler.handle(ResetDbCommand(db_name=db_name))
        await handler.handle(UpdateDbSchemaCommand())

        if appsettings.RESET_DUCK_DB:
            await handler.handle(ResetDuckDbCommand())
        # Initialize DuckDB schema
        await handler.handle(SetupDuckDBSchemaCommand())

        # Seed DB
        hashed_pw = pw_hasher.hash(str(appsettings.ADMIN_PASSWORD))
        await handler.handle(SeedDatabasesCommand(appsettings.ADMIN_EMAIL, hashed_pw))

        # Initialize S3
        if appsettings.ENV == "Development":
            await handler.handle(InitializeS3BucketsCommand())

        yield {
            "command_handler": handler,
            "user": None,
            "session_id": None,
            "ip_address": None,
            "is_privileged": False
        }
