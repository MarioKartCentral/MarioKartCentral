import type { Translation } from '../i18n-types';

const de: Translation = {
  // TODO
  WELCOME: 'Welcome to Mario Kart Central!',
  // TODO
  SUMMARY:
    "We are the home of Mario Kart Tournaments, where you'll find tournaments for all players—whether you're looking for a casual or competitive competition, we've got you covered! We hold events for Mario Kart 8 Deluxe, Tour, and more, with a variety of matches happening weekly!",
  LANGUAGE: 'Deutsch',
  LOGOUT: 'Logout',
  EMAIL: 'Email',
  PASSWORD: 'Password',
  MKC_REGISTRY: 'MKCentral Registry',
  NAVBAR: {
    TOURNAMENTS: 'Tournaments',
    TIME_TRIALS: 'Time Trials',
    LOUNGE: 'Lounge',
    REGISTRY: 'Registry',
    DISCORD: 'Discord',
    TYPE: 'Type',
    IS_READ: 'Is Read',
    LANGUAGE_PICKER: 'Language Picker',
    LOGIN: 'Login',
    REGISTER: 'Register',
    PLAYER_SIGNUP: 'Player Signup',
    PROFILE: 'Profile',
    MENU: 'Menu',
    HOME_PAGE: 'Home Page',
    NOTIFICATIONS: 'Notifications',
    MODERATOR: 'Moderator',
  },
  PLAYER_LIST: {
    PLAYERS: 'Players',
    PLAYER_LISTING: 'Player Listing',
    SEARCH: 'Search',
    FILTERS: {
      ALL_GAMES: 'All Games',
      ALL_COUNTRIES: 'All Countries',
      SEARCH_BY: 'Search by Name or Friend Code...',
      SEARCH: 'Search',
    },
    HEADER: {
      COUNTRY: 'Country',
      NAME: 'Name',
    },
  },
  TEAM_LIST: {
    TAG: 'Tag',
    TEAMS: 'Teams',
    NAME: 'Name',
    STATUS: 'Status',
    GAME: 'Game',
    MODE: 'Mode',
    ROSTERS: 'Rosters',
    REGISTERED: 'Registered',
    CREATE_TEAM: 'Create a team',
    TEAM_LISTING: 'Team Listing',
    SHOW: 'show',
    HIDE: 'hide',
  },
  TEAM_CREATE: {
    GENERAL_INFO: 'General Info',
  },
  TEAM_EDIT: {
    BACK_TO_TEAM: 'Back to Team',
    TEAM_PAGE: 'Team Page',
    TEAM_NAME: 'Team Name',
    TEAM_TAG: 'Team Tag',
    TEAM_COLOR: 'Team Color',
    REQUEST_NAME_TAG_CHANGE: 'Request Name/Tag Change',
    TEAM_LOGO: 'Team Logo',
    TEAM_DESCRIPTION: 'Team Description',
    RECRUITMENT_STATUS: 'Recruitment Status',
    MISC_INFO: 'Misc. Info',
    CUSTOMIZATION: 'Customization',
    NEW_ROSTER: 'New Roster',
    INVITATIONS: 'Invitations',
    INVITE_PLAYER: 'Invite Player',
    RETRACT_INVITE: 'Retract Invite',
    SEARCH_FOR_PLAYERS: 'Search for players...',
    EDIT_ROSTER: 'Edit Roster',
    ROSTER_NAME: 'Roster Name',
    ROSTER_TAG: 'Roster Tag',
  },
  TEAM_PROFILE: {
    TEAM_PROFILE: 'Team Profile',
    MANAGE_ROSTERS: 'Manage Rosters',
    EDIT_TEAM: 'Edit Team',
    REGISTERED: 'Registered',
    MAIN_LANGUAGE: 'Main Language',
    MANAGERS: 'Managers',
    ROSTERS: 'Rosters',
    PLAYER: 'player',
    PLAYERS: 'players',
    JOIN_DATE: 'Join Date',
    RECRUITMENT_STATUS: {
      RECRUITING: 'Recruiting',
      NOT_RECRUITING: 'Not Recruiting',
    },
  },
  // TODO
  PLAYER_PROFILE: {
    PLAYER_PROFILE: 'Player Profile',
    INVITES: 'Invites',
    EDIT_PROFILE: 'Edit Profile',
    DESCRIPTION: 'Description',
    PRIMARY: 'Primary?',
    SUBMIT: 'Submit',
    FRIEND_CODE: 'Friend Code',
    FRIEND_CODES: 'Friend Codes',
    ADD_FRIEND_CODE: 'Add Friend Code',
    AVATAR_URL: 'Avatar URL',
    ABOUT_ME: 'About me',
    LANGUAGE: 'Language',
    THEME: 'Theme',
    TIMEZONE: 'Timezone',
    SAVE: 'Save',
    PLAYER_NOTES: 'Player Notes',
    EDIT_PLAYER_NOTES: 'Edit Player Notes',
    CANCEL: 'Cancel',
    CLEAR: 'Clear',
    NONE: 'None',
  },
  // TODO
  PLAYER_BAN: {
    PLAYER_ID: 'Player ID',
    BANNED_BY: 'Banned By',
    UNBANNED_BY: 'Unbanned By',
    IS_INDEFINITE: 'Is Indefinite',
    BAN_DATE: 'Ban Date',
    DURATION: 'Duration',
    EXPIRATION_DATE: 'Expiration Date',
    EXPIRES: 'Expires',
    REASON: 'Reason',
    COMMENT: 'Comment',
    COMMENT_INCLUDES: 'Comment Includes',
    COMMENT_ONLY_MODS: 'Comment (Only moderators can see this)',
    SUBMIT: 'Submit',
    CANCEL: 'Cancel',
    INDEFINITE: 'Indefinite',
    NUMBER_OF_DAYS: 'Number of Days',
    SELECT_REASON: 'Select Reason',
    BAN_PLAYER: 'Ban Player',
    EDIT_BAN: 'Edit Ban',
    UNBAN: 'Unban',
    BANNED: 'Banned',
    UNBANNED: 'Unbanned',
    VIEW_EDIT_BAN: 'View / Edit Ban',
    BAN_DETAILS: 'Ban Details',
    EDIT_BAN_DETAILS: 'Edit Ban Details',
    ENTER_REASON: 'Enter reason',
    PLAYER: '{{Player|Players}}', // TODO: update "Player" and "Players"
    USER: 'User {userId}',
    THE_PLAYER_IS_ALREADY_BANNED: 'The player is already banned',
    FROM_INITIAL_BAN_DATE: 'From initial ban date',
    LIST_OF_BANNED_PLAYERS: 'List of Banned Players',
    LIST_OF_HISTORICAL_BANS: 'List of Historical Bans',
    COUNT_DAYS: '{count} {{day|days}}', // TODO: update words EXCEPT "count"
    IN_COUNT_DAYS: '(In {count} {{day|days}})', // TODO: update words EXCEPT "count". Example usage: "In 5 days"
    YES: 'Yes',
    NO: 'No',
    STAFF: 'STAFF',
    SEARCH: 'Search',
    NAME: 'Name',
    BANNED_TO: 'Banned To',
    BANNED_FROM: 'Banned From',
    UNBANNED_TO: 'Unbanned To',
    UNBANNED_FROM: 'Unbanned From',
    EXPIRES_TO: 'Expires To',
    EXPIRES_FROM: 'Expires From',
    SEARCH_BY_NAME: 'Search by Name',
    THIS_PLAYER_IS_BANNED: 'This player is <strong>banned</strong> and may not participate in MKCentral competitions.',
    UNBAN_DATE: 'Unban Date',
  },
  LANGUAGES: {
    EN_US: 'English (United States)',
    EN_GB: 'English (Great Britain)',
    DE: 'German',
    ES: 'Spanish',
    FR: 'French',
    JA: 'Japanese',
  },
  COLORS: {
    RED_1: 'Red 1',
    RED_2: 'Red 2',
    RED_3: 'Red 3',
    RED_4: 'Red 4',
    ORANGE_1: 'Orange 1',
    ORANGE_2: 'Orange 2',
    ORANGE_3: 'Orange 3',
    ORANGE_4: 'Orange 4',
    YELLOW_1: 'Yellow 1',
    YELLOW_2: 'Yellow 2',
    YELLOW_3: 'Yellow 3',
    YELLOW_4: 'Yellow 4',
    GREEN_1: 'Green 1',
    GREEN_2: 'Green 2',
    GREEN_3: 'Green 3',
    GREEN_4: 'Green 4',
    AQUA_1: 'Aqua 1',
    AQUA_2: 'Aqua 2',
    AQUA_3: 'Aqua 3',
    AQUA_4: 'Aqua 4',
    BLUE_1: 'Blue 1',
    BLUE_2: 'Blue 2',
    BLUE_3: 'Blue 3',
    BLUE_4: 'Blue 4',
    INDIGO_1: 'Indigo 1',
    INDIGO_2: 'Indigo 2',
    INDIGO_3: 'Indigo 3',
    INDIGO_4: 'Indigo 4',
    PURPLE_1: 'Purple 1',
    PURPLE_2: 'Purple 2',
    PURPLE_3: 'Purple 3',
    PURPLE_4: 'Purple 4',
    PINK_1: 'Pink 1',
    PINK_2: 'Pink 2',
    PINK_3: 'Pink 3',
    PINK_4: 'Pink 4',
    GREY_1: 'Grey 1',
    GREY_2: 'Grey 2',
    GREY_3: 'Grey 3',
    BLACK: 'Black',
  },
  NOTIFICATION: {
    MARK_ALL_READ: 'Mark All as Read',
    SEE_ALL_NOTIFICATIONS: 'See All Notifications',
    NO_UNREAD: 'There are no unread notifications',
    MUST_BE_LOGGED_IN: 'You must be logged in to view this page.',
    NO_NOTIFICATIONS: 'You do not have any notifications.',
    MARK_READ: 'Mark As Read',
    MARK_UNREAD: 'Mark As Unread',
  },
  // TODO
  // Unless there is a TODO comment on a specific line, you shouldn't have to edit anything inside {}
  // since they are variables used by i18n and are not part of the sentence translation.
  // For example, if a line contains "Reason: {reason|bold}", you would only translate the
  // word "Reason" and you shouldn't change "{reason|bold}"
  NOTIFICATION_CONTENT: {
    '0': 'You have been banned and may not participate in MKCentral competitions. Reason: {reason|bold}. Unban Date: {date|parsedate|bold}',
    '1': 'You have been unbanned and may now participate in MKCentral competitions.',
    '2': 'You have been invited to {squad_name|{: a, *: the}} squad {squad_name|bold} for {tournament_name|bold}!', // TODO: in "{: a, *: the}", update "a" and "the". Context: "You have been invited to a squad" or "You have been invited to the squad"
    '3': '{player_name|bold} accepted their invitation to your {tournament_name|bold} squad!',
    '4': 'You have been kicked from {squad_name|bold}.',
    '5': 'A moderator has registered you for {tournament_name|bold}!',
    '6': 'A moderator has unregistered you from {tournament_name|bold}.',
    '7': 'A moderator added {player_name|bold} to your {tournament_name|bold} squad.',
    '8': 'A moderator kicked {player_name|bold} from your {tournament_name|bold} squad.',
    '9': 'You have been invited to {roster_name|bold}!',
    '10': '{player_name|bold} accepted their invitation to {roster_name|bold}. A moderator must approve this before they can play for your team.',
    '11': '{player_name|bold} declined their invitation to {roster_name|bold}.',
    '12': 'You have been kicked from {roster_name|bold}.',
    '13': 'Your team {team_name|bold} has been approved!',
    '14': 'Your team {team_name|bold} has been denied.',
    '15': '{player_name|bold} has joined {roster_name|bold}!',
    '16': 'A moderator has denied {player_name|bold} from joining {roster_name|bold}.',
    '17': '{player_name|bold} has left {roster_name|bold}.',
    '18': 'Your team name/tag change for {team_name|bold} has been approved!',
    '19': 'Your team name/tag change for {team_name|bold} has been denied.',
    '20': 'Your team roster name/tag change for {roster_name|bold} has been approved!',
    '21': 'Your team roster name/tag change for {roster_name|bold} has been denied.',
    '22': 'A moderator has added a friend code to your profile. Game: {game|uppercase|bold}.',
    '23': 'A moderator has edited your {game|uppercase|bold} friend code.',
    '24': 'A moderator has set your primary friend code.',
    '25': 'Your name change has been approved!',
    '26': 'Your name change has been denied.',
    '27': 'You have been given the {role|bold} role!',
    '28': 'Your {role|bold} role has been removed.',
    '29': 'You have been given the {role|bold} role for the team {team_name|bold}.',
    '30': 'Your {role|bold} role for the team {team_name|bold} has been removed.',
    '31': 'You have been given the {role|bold} role for the {series_name|bold} series.',
    '32': 'Your {role|bold} role for the {series_name|bold} series has been removed.',
    '33': 'You have been given the {role|bold} role for the {tournament_name|bold} tournament.',
    '34': 'Your {role|bold} role for the {tournament_name|bold} tournament has been removed.',
    '35': 'Your roster {roster_name|bold} has been approved!',
    '36': 'Your roster {roster_name|bold} has been denied.',
    '37': 'You have been made the squad captain for {squad_name|bold}!',
    '38': 'You have been made a team representative for {squad_name|bold}!',
    '39': 'You are no longer a team representative for {squad_name|bold}.',
    '40': 'A moderator has updated your team {team_name|bold}.',
    '41': 'A moderator has updated your roster {roster_name|bold}.',
    '42': 'A moderator has registered your team for {tournament_name|bold}!',
    '43': 'A moderator has unregistered your team from {tournament_name|bold}.',
    '44': 'A moderator has created a squad with you as the captain for {tournament_name|bold}!',
    '45': 'A moderator has updated your registration for {tournament_name|bold}.',
    '46': 'A moderator has approved your team transfer to {roster_name|bold}!',
    '47': 'Your team transfer to {roster_name|bold} has been denied.',
    '48': 'Your ban has been updated. Reason: {reason|bold}. Unban Date: {date|parsedate|bold}',
    '49': 'A moderator has kicked {player_name|bold} from your team {team_name|bold}.',
    '50': '{player_name|bold} declined their invitation to {squad_name|bold}.',
  },
  COUNTRIES: {
    AF: 'Afghanistan',
    AX: 'Åland',
    AL: 'Albanien',
    DZ: 'Algerien',
    AS: 'Amerikanisch-Samoa',
    AD: 'Andorra',
    AO: 'Angola',
    AI: 'Anguilla',
    AQ: 'Antarktis (Sonderstatus durch Antarktisvertrag)',
    AG: 'Antigua und Barbuda',
    AR: 'Argentinien',
    AM: 'Armenien',
    AW: 'Aruba',
    AU: 'Australien',
    AT: 'Österreich',
    AZ: 'Aserbaidschan',
    BS: 'Bahamas',
    BH: 'Bahrain',
    BD: 'Bangladesch',
    BB: 'Barbados',
    BY: 'Belarus',
    BE: 'Belgien',
    BZ: 'Belize',
    BJ: 'Benin',
    BM: 'Bermuda',
    BT: 'Bhutan',
    BO: 'Bolivien',
    BQ: 'Bonaire, Saba, Sint Eustatius',
    BA: 'Bosnien und Herzegowina',
    BW: 'Botswana',
    BV: 'Bouvetinsel',
    BR: 'Brasilien',
    IO: 'Britisches Territorium im Indischen Ozean',
    BN: 'Brunei',
    BG: 'Bulgarien',
    BF: 'Burkina Faso',
    BI: 'Burundi',
    KH: 'Kambodscha',
    CM: 'Kamerun',
    CA: 'Kanada',
    CV: 'Kap Verde',
    KY: 'Kaimaninseln',
    CF: 'Zentralafrikanische Republik',
    TD: 'Tschad',
    CL: 'Chile',
    CN: 'China, Volksrepublik',
    CX: 'Weihnachtsinsel',
    CC: 'Kokosinseln',
    CO: 'Kolumbien',
    KM: 'Komoren',
    CG: 'Kongo, Republik',
    CD: 'Kongo, Demokratische Republik',
    CK: 'Cookinseln',
    CR: 'Costa Rica',
    CI: 'Elfenbeinküste',
    HR: 'Kroatien',
    CU: 'Kuba',
    CW: 'Curaçao',
    CY: 'Zypern',
    CZ: 'Tschechien',
    DK: 'Dänemark',
    DJ: 'Dschibuti',
    DM: 'Dominica',
    DO: 'Dominikanische Republik',
    EC: 'Ecuador',
    EG: 'Ägypten',
    SV: 'El Salvador',
    GQ: 'Äquatorialguinea',
    ER: 'Eritrea',
    EE: 'Estland',
    ET: 'Äthiopien',
    FK: 'Falklandinseln',
    FO: 'Färöer',
    FJ: 'Fidschi',
    FI: 'Finnland',
    FR: 'Frankreich',
    GF: 'Französisch-Guayana',
    PF: 'Französisch-Polynesien',
    TF: 'Französische Süd- und Antarktisgebiete',
    GA: 'Gabun',
    GM: 'Gambia',
    GE: 'Georgien',
    DE: 'Deutschland',
    GH: 'Ghana',
    GI: 'Gibraltar',
    GR: 'Griechenland',
    GL: 'Grönland',
    GD: 'Grenada',
    GP: 'Guadeloupe',
    GU: 'Guam',
    GT: 'Guatemala',
    GG: 'Guernsey (Kanalinsel)',
    GN: 'Guinea',
    GW: 'Guinea-Bissau',
    GY: 'Guyana',
    HT: 'Haiti',
    HM: 'Heard und McDonaldinseln',
    VA: 'Vatikanstadt',
    HN: 'Honduras',
    HK: 'Hongkong',
    HU: 'Ungarn',
    IS: 'Island',
    IN: 'Indien',
    ID: 'Indonesien',
    IR: 'Iran',
    IQ: 'Irak',
    IE: 'Irland',
    IM: 'Insel Man',
    IL: 'Israel',
    IT: 'Italien',
    JM: 'Jamaika',
    JP: 'Japan',
    JE: 'Jersey (Kanalinsel)',
    JO: 'Jordanien',
    KZ: 'Kasachstan',
    KE: 'Kenia',
    KI: 'Kiribati',
    KP: 'Korea, Nord (Nordkorea)',
    KR: 'Korea, Süd (Südkorea)',
    KW: 'Kuwait',
    KG: 'Kirgisistan',
    LA: 'Laos',
    LV: 'Lettland',
    LB: 'Libanon',
    LS: 'Lesotho',
    LR: 'Liberia',
    LY: 'Libyen',
    LI: 'Liechtenstein',
    LT: 'Litauen',
    LU: 'Luxemburg',
    MO: 'Macau',
    MK: 'Nordmazedonien',
    MG: 'Madagaskar',
    MW: 'Malawi',
    MY: 'Malaysia',
    MV: 'Malediven',
    ML: 'Mali',
    MT: 'Malta',
    MH: 'Marshallinseln',
    MQ: 'Martinique',
    MR: 'Mauretanien',
    MU: 'Mauritius',
    YT: 'Mayotte',
    MX: 'Mexiko',
    FM: 'Mikronesien',
    MA: 'Marokko',
    MD: 'Moldau',
    MC: 'Monaco',
    MN: 'Mongolei',
    ME: 'Montenegro',
    MS: 'Montserrat',
    MZ: 'Mosambik',
    MM: 'Myanmar',
    NA: 'Namibia',
    NR: 'Nauru',
    NP: 'Nepal',
    NL: 'Niederlande',
    NC: 'Neukaledonien',
    NZ: 'Neuseeland',
    NI: 'Nicaragua',
    NE: 'Niger',
    NG: 'Nigeria',
    NU: 'Niue',
    NF: 'Norfolkinsel',
    MP: 'Nördliche Marianen',
    NO: 'Norwegen',
    OM: 'Oman',
    PK: 'Pakistan',
    PW: 'Palau',
    PS: 'Palästina',
    PA: 'Panama',
    PG: 'Papua-Neuguinea',
    PY: 'Paraguay',
    PE: 'Peru',
    PH: 'Philippinen',
    PN: 'Pitcairninseln',
    PL: 'Polen',
    PT: 'Portugal',
    PR: 'Puerto Rico',
    QA: 'Katar',
    RE: 'Réunion',
    RO: 'Rumänien',
    RU: 'Russland',
    RW: 'Ruanda',
    BL: 'Saint-Barthélemy',
    SH: 'St. Helena, Ascension und Tristan da Cunha',
    KN: 'St. Kitts und Nevis',
    LC: 'St. Lucia',
    MF: 'Saint-Martin (französischer Teil)',
    PM: 'Saint-Pierre und Miquelon',
    VC: 'St. Vincent und die Grenadinen',
    WS: 'Samoa',
    SM: 'San Marino',
    ST: 'São Tomé und Príncipe',
    SA: 'Saudi-Arabien',
    SN: 'Senegal',
    RS: 'Serbien',
    SC: 'Seychellen',
    SL: 'Sierra Leone',
    SG: 'Singapur',
    SX: 'Sint Maarten',
    SK: 'Slowakei',
    SI: 'Slowenien',
    SB: 'Salomonen',
    SO: 'Somalia',
    ZA: 'Südafrika',
    GS: 'Südgeorgien und die Südlichen Sandwichinseln',
    SS: 'Südsudan',
    ES: 'Spanien',
    LK: 'Sri Lanka',
    SD: 'Sudan',
    SR: 'Suriname',
    SJ: 'Spitzbergen und Jan Mayen',
    SZ: 'Eswatini',
    SE: 'Schweden',
    CH: 'Schweiz',
    SY: 'Syrien',
    TW: 'China, Republik',
    TJ: 'Tadschikistan',
    TZ: 'Tansania',
    TH: 'Thailand',
    TL: 'Osttimor',
    TG: 'Togo',
    TK: 'Tokelau',
    TO: 'Tonga',
    TT: 'Trinidad und Tobago',
    TN: 'Tunesien',
    TR: 'Türkei',
    TM: 'Turkmenistan',
    TC: 'Turks- und Caicosinseln',
    TV: 'Tuvalu',
    UG: 'Uganda',
    UA: 'Ukraine',
    AE: 'Vereinigte Arabische Emirate',
    GB: 'Vereinigtes Königreich',
    US: 'Vereinigte Staaten',
    UM: 'United States Minor Outlying Islands',
    UY: 'Uruguay',
    UZ: 'Usbekistan',
    VU: 'Vanuatu',
    VE: 'Venezuela',
    VN: 'Vietnam',
    VG: 'Britische Jungferninseln',
    VI: 'Amerikanische Jungferninseln',
    WF: 'Wallis und Futuna',
    EH: 'Westsahara',
    YE: 'Jemen',
    ZM: 'Sambia',
    ZW: 'Simbabwe',
  },
};

export default de;
