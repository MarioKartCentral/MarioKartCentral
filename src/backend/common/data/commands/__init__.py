from common.data.command import Command as Command

from common.data.commands.auth.api_tokens import *
from common.data.commands.auth.discord import *
from common.data.commands.auth.permissions import *
from common.data.commands.auth.roles import *
from common.data.commands.auth.seriesroles import *
from common.data.commands.auth.sessions import *
from common.data.commands.auth.teamroles import *
from common.data.commands.auth.tournamentroles import *

from common.data.commands.emails.emails import *

from common.data.commands.moderation.alt_detection import *
from common.data.commands.moderation.mod_notifications import *
from common.data.commands.moderation.player_bans import *
from common.data.commands.moderation.word_filter import *

from common.data.commands.players.claims import *
from common.data.commands.players.friend_codes import *
from common.data.commands.players.lounge import *
from common.data.commands.players.name_changes import *
from common.data.commands.players.notes import *
from common.data.commands.players.players import *

from common.data.commands.posts.posts import *

from common.data.commands.system.db_admin import *
from common.data.commands.system.db_backup import *
from common.data.commands.system.duckdb_admin import *
from common.data.commands.system.s3_admin import *
from common.data.commands.system.v1_migration import *

from common.data.commands.teams.invitations import *
from common.data.commands.teams.rosters import *
from common.data.commands.teams.teams import *
from common.data.commands.teams.transfers import *

from common.data.commands.time_trials.time_trials import *

from common.data.commands.tournaments.placements import *
from common.data.commands.tournaments.registrations import *
from common.data.commands.tournaments.series import *
from common.data.commands.tournaments.squads import *
from common.data.commands.tournaments.templates import *
from common.data.commands.tournaments.tournaments import *

from common.data.commands.user_activity.compression import *
from common.data.commands.user_activity.queue import *

from common.data.commands.users.notifications import *
from common.data.commands.users.settings import *
from common.data.commands.users.users import *

from common.data.commands.worker.job_state import *