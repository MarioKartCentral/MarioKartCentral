from dataclasses import dataclass
from typing import List, Literal

@dataclass
class XFUser:
    user_id: int
    username: str
    email: str
    register_date: int
    is_banned: Literal[0, 1]

@dataclass
class XFUserAuthenticate:
    user_id: int
    data: str # contains a serialized PHP object with a property called "hash" that contains a bcrypt hash of the user's password

@dataclass
class XFUserBan:
    user_id: int
    ban_date: int
    end_date: int
    user_reason: str | None

@dataclass
class XenforoData:
    xf_user: List[XFUser]
    xf_user_authenticate: List[XFUserAuthenticate]
    xf_user_ban: List[XFUserBan]

@dataclass
class MKCEventPlacement:
    id: int
    event_registration_id: int
    placement: int
    disqualified: Literal[0, 1]
    title: str | None

@dataclass
class MKCEventRegistration:
    id: int
    event_id: int
    player_id: int
    status: Literal["registered", "withdrawn", "rejected"]
    created_at: str # timestamp
    updated_at: str # timestamp
    player_can_host: Literal[0, 1]
    team_id: int | None
    mii_name: str | None
    squad_id: int | None
    checked_in: Literal[0, 1]
    verified: Literal[0, 1]

MKCGameMode = Literal["mk7_vs_race", "mk8dx_150", "mk8dx_200", "mk8dx_battle_bobomb", "mk8dx_battle_coin", "mk8dx_battle_shine", "mk8dx_mixed", "mk8u_150", "mk8u_200", "mktour_vs_race", "mkw_vs_race", "smk_match_race", "switch_other"]

@dataclass
class MKCEvent:
    id: int
    title: str
    start_date: str | None # timestamp
    end_date: str | None # timestamp
    event_format: Literal["0", "1", "2"] # not sure what these numbers represent
    minimum_team_size: int
    game_mode: MKCGameMode
    description: str
    rules: str
    published: Literal[0, 1]
    registrations_open: Literal[0, 1]
    maximum_team_size: int
    team_tag_required: Literal[0, 1]
    team_name_required: Literal[0, 1]
    transfer_date: str | None # timestamp
    show_on_profiles: Literal[0, 1]
    player_host_required: Literal[0, 1]
    player_mii_name_required: Literal[0, 1]
    team_mode: Literal["200cc", "150cc", "mk8u_150cc", "mktour_vs", "mk7_vs", "mkw_vs", "mk8u_200cc"] | None
    total_registrations_override: int | None
    pr_value: int
    post_registration_message: str | None
    checkin_required: Literal[0, 1]
    checkin_status: Literal[0, 1, 2]
    verification_required: Literal[0, 1]
    checkin_minimum: int
    tournament_series_id: int | None
    logo_filename: str | None
    organizer: str
    location: str | None
    series_stats_include: Literal[0, 1]

@dataclass
class MKCPlayerBan:
    id: int
    player_id: int
    banned_by: int # player id
    start_date: str # timestamp
    end_date: str | None # timestamp
    reason: str

@dataclass
class MKCPlayerOptout:
    id: int
    event_registration_id: int
    player_id: int
    created_at: str # timestamp

@dataclass
class MKCPlayerRole:
    id: int
    player_id: int
    role: str # administrate | event_admin | event_mod | moderate | supporter | series_admin:<N> | series_mod:<N>

@dataclass
class MKCPlayer:
    id: int
    user_id: int | None # xenforo user id
    display_name: str
    country: str
    region: str | None
    city: str | None
    switch_fc: str | None
    created_at: str # timestamp
    updated_at: str # timestamp
    profile_message: str
    discord_tag: str | None
    discord_privacy: Literal["private", "public"]
    is_hidden: Literal[0, 1]
    mktour_fc: str | None
    fc_3ds: str | None
    nnid: str | None

@dataclass
class MKCSquadMembership:
    id: int
    player_id: int
    squad_id: int
    captain: Literal[0, 1]
    status: Literal["registered", "cancelled", "declined", "withdrawn", "kicked", "invited", "rejected"]
    created_at: str # timestamp
    updated_at: str # timestamp
    player_can_host: Literal[0, 1]
    mii_name: str | None
    checked_in: Literal[0, 1]

@dataclass
class MKCSquad:
    id: int
    squad_name: str
    squad_tag: str
    color_number: int
    created_at: str # timestamp
    is_shadow: Literal[0, 1]

@dataclass
class MKCTeamMembership:
    id: int
    player_id: int
    team_id: int
    joined: str # timestamp
    left: str | None # timestamp
    team_leader: Literal[0, 1]
    roster_category: Literal["150cc", "200cc", "mktour_vs"]

@dataclass
class MKCTeamRepresentative:
    id: int
    player_id: int
    event_registration_id: int

@dataclass
class MKCTeamRosters:
    id: int
    team_id: int
    roster_category: Literal["150cc", "200cc", "mktour_vs"]
    roster_active: Literal[0, 1]
    roster_name: str | None

@dataclass
class MKCTeam:
    id: int
    team_name: str
    team_tag: str
    picture_filename: str
    team_description: str
    created_at: str # timestamp
    updated_at: str # timestamp
    status: Literal["approved", "banned", "disapproved"]
    recruitment_status: Literal["recruiting", "closed", "invite_only"]
    main_language: str
    is_historical: Literal[0, 1]
    color_number: int
    team_category: Literal["150cc", "200cc", "mk7_vs", "mk8u_150cc", "mk8u_200cc", "mktour_vs", "mkw_vs"]
    manager_player_id: int | None
    is_shadow: Literal[0, 1]
    primary_team_id: int | None

@dataclass
class MKCTournamentSeries:
    id: int
    series_name: str
    url_slug: str
    display_order: int
    logo_filename: str
    default_event_format: Literal["0", "1", "2"] | None
    default_game_mode: MKCGameMode | None
    full_description: str | None
    short_description: str
    created_at: str # timestamp
    updated_at: str # timestamp
    published: Literal[0, 1]
    historical: Literal[0, 1]
    stats_aggregation_field: Literal["team_id", "player_id", "squad_name"] | None
    finalist_criteria: Literal["top_2", "top_3_or_finalist"] | None
    organizer: Literal["mkc", "affiliate", "lan"]
    location: str | None

@dataclass
class MKCData:
    event_placements: List[MKCEventPlacement]
    event_registrations: List[MKCEventRegistration]
    events: List[MKCEvent]
    player_bans: List[MKCPlayerBan]
    player_optouts: List[MKCPlayerOptout]
    player_roles: List[MKCPlayerRole]
    players: List[MKCPlayer]
    squad_memberships: List[MKCSquadMembership]
    squads: List[MKCSquad]
    team_memberships: List[MKCTeamMembership]
    team_representatives: List[MKCTeamRepresentative]
    team_rosters: List[MKCTeamRosters]
    teams: List[MKCTeam]
    tournament_series: List[MKCTournamentSeries]

@dataclass
class MKCV1Data:
    xf: XenforoData
    mkc: MKCData