import type { Translation } from '../i18n-types';

const ja: Translation = {
  // TODO
  WELCOME: 'Welcome to Mario Kart Central!',
  // TODO
  SUMMARY:
    "We are the home of Mario Kart Tournaments, where you'll find tournaments for all players—whether you're looking for a casual or competitive competition, we've got you covered! We hold events for Mario Kart 8 Deluxe, Tour, and more, with a variety of matches happening weekly!",
  LANGUAGE: '日本語',
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
  // TODO
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
    '51': 'Your claim of shadow player {player_name|bold} has been accepted!',
    '52': 'Your claim of shadow player {player_name|bold} has been denied.',
  },
  COUNTRIES: {
    AF: 'アフガニスタン',
    AX: 'オーランド諸島',
    AL: 'アルバニア',
    DZ: 'アルジェリア',
    AS: 'アメリカ領サモア',
    AD: 'アンドラ',
    AO: 'アンゴラ',
    AI: 'アンギラ',
    AQ: '南極',
    AG: 'アンティグア・バーブーダ',
    AR: 'アルゼンチン',
    AM: 'アルメニア',
    AW: 'アルバ',
    AU: 'オーストラリア',
    AT: 'オーストリア',
    AZ: 'アゼルバイジャン',
    BS: 'バハマ',
    BH: 'バーレーン',
    BD: 'バングラデシュ',
    BB: 'バルバドス',
    BY: 'ベラルーシ',
    BE: 'ベルギー',
    BZ: 'ベリーズ',
    BJ: 'ベナン',
    BM: 'バミューダ',
    BT: 'ブータン',
    BO: 'ボリビア多民族国',
    BQ: 'ボネール、シント・ユースタティウスおよびサバ',
    BA: 'ボスニア・ヘルツェゴビナ',
    BW: 'ボツワナ',
    BV: 'ブーベ島',
    BR: 'ブラジル',
    IO: 'イギリス領インド洋地域',
    BN: 'ブルネイ・ダルサラーム',
    BG: 'ブルガリア',
    BF: 'ブルキナファソ',
    BI: 'ブルンジ',
    KH: 'カンボジア',
    CM: 'カメルーン',
    CA: 'カナダ',
    CV: 'カーボベルデ',
    KY: 'ケイマン諸島',
    CF: '中央アフリカ共和国',
    TD: 'チャド',
    CL: 'チリ',
    CN: '中華人民共和国',
    CX: 'クリスマス島',
    CC: 'ココス（キーリング）諸島',
    CO: 'コロンビア',
    KM: 'コモロ',
    CG: 'コンゴ共和国',
    CD: 'コンゴ民主共和国',
    CK: 'クック諸島',
    CR: 'コスタリカ',
    CI: 'コートジボワール',
    HR: 'クロアチア',
    CU: 'キューバ',
    CW: 'キュラソー',
    CY: 'キプロス',
    CZ: 'チェコ',
    DK: 'デンマーク',
    DJ: 'ジブチ',
    DM: 'ドミニカ国',
    DO: 'ドミニカ共和国',
    EC: 'エクアドル',
    EG: 'エジプト',
    SV: 'エルサルバドル',
    GQ: '赤道ギニア',
    ER: 'エリトリア',
    EE: 'エストニア',
    ET: 'エチオピア',
    FK: 'フォークランド（マルビナス）諸島',
    FO: 'フェロー諸島',
    FJ: 'フィジー',
    FI: 'フィンランド',
    FR: 'フランス',
    GF: 'フランス領ギアナ',
    PF: 'フランス領ポリネシア',
    TF: 'フランス領南方・南極地域',
    GA: 'ガボン',
    GM: 'ガンビア',
    GE: 'ジョージア',
    DE: 'ドイツ',
    GH: 'ガーナ',
    GI: 'ジブラルタル',
    GR: 'ギリシャ',
    GL: 'グリーンランド',
    GD: 'グレナダ',
    GP: 'グアドループ',
    GU: 'グアム',
    GT: 'グアテマラ',
    GG: 'ガーンジー',
    GN: 'ギニア',
    GW: 'ギニアビサウ',
    GY: 'ガイアナ',
    HT: 'ハイチ',
    HM: 'ハード島とマクドナルド諸島',
    VA: 'バチカン市国',
    HN: 'ホンジュラス',
    HK: '香港',
    HU: 'ハンガリー',
    IS: 'アイスランド',
    IN: 'インド',
    ID: 'インドネシア',
    IR: 'イラン・イスラム共和国',
    IQ: 'イラク',
    IE: 'アイルランド',
    IM: 'マン島',
    IL: 'イスラエル',
    IT: 'イタリア',
    JM: 'ジャマイカ',
    JP: '日本',
    JE: 'ジャージー',
    JO: 'ヨルダン',
    KZ: 'カザフスタン',
    KE: 'ケニア',
    KI: 'キリバス',
    KP: '朝鮮民主主義人民共和国',
    KR: '大韓民国',
    KW: 'クウェート',
    KG: 'キルギス',
    LA: 'ラオス人民民主共和国',
    LV: 'ラトビア',
    LB: 'レバノン',
    LS: 'レソト',
    LR: 'リベリア',
    LY: 'リビア',
    LI: 'リヒテンシュタイン',
    LT: 'リトアニア',
    LU: 'ルクセンブルク',
    MO: 'マカオ',
    MK: '北マケドニア',
    MG: 'マダガスカル',
    MW: 'マラウイ',
    MY: 'マレーシア',
    MV: 'モルディブ',
    ML: 'マリ',
    MT: 'マルタ',
    MH: 'マーシャル諸島',
    MQ: 'マルティニーク',
    MR: 'モーリタニア',
    MU: 'モーリシャス',
    YT: 'マヨット',
    MX: 'メキシコ',
    FM: 'ミクロネシア連邦',
    MA: 'モロッコ',
    MD: 'モルドバ共和国',
    MC: 'モナコ',
    MN: 'モンゴル',
    ME: 'モンテネグロ',
    MS: 'モントセラト',
    MZ: 'モザンビーク',
    MM: 'ミャンマー',
    NA: 'ナミビア',
    NR: 'ナウル',
    NP: 'ネパール',
    NL: 'オランダ',
    NC: 'ニューカレドニア',
    NZ: 'ニュージーランド',
    NI: 'ニカラグア',
    NE: 'ニジェール',
    NG: 'ナイジェリア',
    NU: 'ニウエ',
    NF: 'ノーフォーク島',
    MP: '北マリアナ諸島',
    NO: 'ノルウェー',
    OM: 'オマーン',
    PK: 'パキスタン',
    PW: 'パラオ',
    PS: 'パレスチナ',
    PA: 'パナマ',
    PG: 'パプアニューギニア',
    PY: 'パラグアイ',
    PE: 'ペルー',
    PH: 'フィリピン',
    PN: 'ピトケアン',
    PL: 'ポーランド',
    PT: 'ポルトガル',
    PR: 'プエルトリコ',
    QA: 'カタール',
    RE: 'レユニオン',
    RO: 'ルーマニア',
    RU: 'ロシア連邦',
    RW: 'ルワンダ',
    BL: 'サン・バルテルミー',
    SH: 'セントヘレナ・アセンションおよびトリスタンダクーニャ',
    KN: 'セントクリストファー・ネイビス',
    LC: 'セントルシア',
    MF: 'サン・マルタン（フランス領）',
    PM: 'サンピエール島・ミクロン島',
    VC: 'セントビンセントおよびグレナディーン諸島',
    WS: 'サモア',
    SM: 'サンマリノ',
    ST: 'サントメ・プリンシペ',
    SA: 'サウジアラビア',
    SN: 'セネガル',
    RS: 'セルビア',
    SC: 'セーシェル',
    SL: 'シエラレオネ',
    SG: 'シンガポール',
    SX: 'シント・マールテン（オランダ領）',
    SK: 'スロバキア',
    SI: 'スロベニア',
    SB: 'ソロモン諸島',
    SO: 'ソマリア',
    ZA: '南アフリカ',
    GS: 'サウスジョージア・サウスサンドウィッチ諸島',
    SS: '南スーダン',
    ES: 'スペイン',
    LK: 'スリランカ',
    SD: 'スーダン',
    SR: 'スリナム',
    SJ: 'スヴァールバル諸島およびヤンマイエン島',
    SZ: 'エスワティニ',
    SE: 'スウェーデン',
    CH: 'スイス',
    SY: 'シリア・アラブ共和国',
    TW: '台湾（中華民国）',
    TJ: 'タジキスタン',
    TZ: 'タンザニア',
    TH: 'タイ',
    TL: '東ティモール',
    TG: 'トーゴ',
    TK: 'トケラウ',
    TO: 'トンガ',
    TT: 'トリニダード・トバゴ',
    TN: 'チュニジア',
    TR: 'トルコ',
    TM: 'トルクメニスタン',
    TC: 'タークス・カイコス諸島',
    TV: 'ツバル',
    UG: 'ウガンダ',
    UA: 'ウクライナ',
    AE: 'アラブ首長国連邦',
    GB: 'イギリス',
    US: 'アメリカ合衆国',
    UM: '合衆国領有小離島',
    UY: 'ウルグアイ',
    UZ: 'ウズベキスタン',
    VU: 'バヌアツ',
    VE: 'ベネズエラ・ボリバル共和国',
    VN: 'ベトナム',
    VG: 'イギリス領ヴァージン諸島',
    VI: 'アメリカ領ヴァージン諸島',
    WF: 'ウォリス・フツナ',
    EH: '西サハラ',
    YE: 'イエメン',
    ZM: 'ザンビア',
    ZW: 'ジンバブエ',
  },
};

export default ja;
