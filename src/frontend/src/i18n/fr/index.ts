import type { Translation } from '../i18n-types';

const fr: Translation = {
  // TODO
  WELCOME: 'Bienvenue Mario Kart Central!',
  // TODO
  SUMMARY:
    'Nous somme le cœur des Compétitions Mario Kart, où vous trouverez des tournois pour tout type de joueurs que vous soyez un joueur occasionnel ou un joueur compétitif, nous sommes là! Nous organisons des tournois sur Mario Kart 8 Deluxe, Tour, et plus encore, avec une variété de matchs qui ont lieu chaque semaine!',
  LANGUAGE: 'Français',
  LOGOUT: 'Se Déconnecter',
  EMAIL: 'Adresse e-mail',
  PASSWORD: 'Mot de passe',
  MKC_REGISTRY: 'Registre MKCentral',
  NAVBAR: {
    TOURNAMENTS: 'Compétitions',
    TIME_TRIALS: 'Contre-la-montre',
    LOUNGE: 'Lounge',
    REGISTRY: 'Registre',
    DISCORD: 'Discord',
    TYPE: 'Type',
    IS_READ: 'Is Read',
    LANGUAGE_PICKER: 'Séléction de la Langue',
    LOGIN: 'Se Connecter',
    REGISTER: "S'inscrire",
    PLAYER_SIGNUP: 'Inscription de Joueur',
    PROFILE: 'Profil',
    MENU: 'Menu',
    HOME_PAGE: "Page d'Acceuil",
    NOTIFICATIONS: 'Notifications',
    MODERATOR: 'Modérateur',
  },
  PLAYER_LIST: {
    PLAYERS: 'Joueurs',
    PLAYER_LISTING: 'Liste des joueurs',
    SEARCH: 'Chercher',
    FILTERS: {
      ALL_GAMES: 'Tous les jeux',
      ALL_COUNTRIES: 'Tous les pays',
      SEARCH_BY: 'Chercher par pseudo ou par code ami...',
      SEARCH: 'Chercher',
    },
    HEADER: {
      COUNTRY: 'Pays',
      NAME: 'Pseudonyme',
    },
  },
  TEAM_LIST: {
    TAG: 'Tag',
    TEAMS: 'Équipes',
    NAME: 'Nom',
    STATUS: 'Statut',
    GAME: 'Jeu',
    MODE: 'Mode',
    ROSTERS: 'Équipes',
    REGISTERED: 'Inscrite',
    CREATE_TEAM: 'Créer une équipe',
    TEAM_LISTING: 'Liste des équipes',
    SHOW: 'voir',
    HIDE: 'cacher',
  },
  TEAM_CREATE: {
    GENERAL_INFO: 'Informations Générales',
  },
  TEAM_EDIT: {
    BACK_TO_TEAM: "Retour à l'Équipe",
    TEAM_PAGE: "Page de l'Équipe",
    TEAM_NAME: "Nom de l'Équipe",
    TEAM_TAG: "Tag de l'Équipe",
    TEAM_COLOR: "Couleur  de l'Équipe",
    REQUEST_NAME_TAG_CHANGE: 'Demander un changement de Nom/Tag',
    TEAM_LOGO: "Logo de l'équipe",
    TEAM_DESCRIPTION: "Déscription de l'Équipe",
    RECRUITMENT_STATUS: 'Statut du Recrutement',
    MISC_INFO: 'Informations Diverses',
    CUSTOMIZATION: 'Customisation',
    NEW_ROSTER: 'Nouvel Effectif',
    INVITATIONS: 'Invitations',
    INVITE_PLAYER: 'Inviter un Joueur',
    RETRACT_INVITE: "Rétracter l'Invitation",
    SEARCH_FOR_PLAYERS: 'Rechercher des joueurs...',
    EDIT_ROSTER: "Modifier l'Effectif",
    ROSTER_NAME: "Nom de l'Effectif",
    ROSTER_TAG: "Tag de l'Effectif",
  },
  TEAM_PROFILE: {
    TEAM_PROFILE: "Profil de l'Équipe",
    MANAGE_ROSTERS: 'Gérer les Effectifs',
    EDIT_TEAM: "Gérer l'Équipe",
    REGISTERED: 'Date de création',
    MAIN_LANGUAGE: 'Langue Principale',
    MANAGERS: 'Managers',
    ROSTERS: 'Effectifs',
    PLAYER: 'joueur',
    PLAYERS: 'joueurs',
    JOIN_DATE: "Date d'Arrivée",
    RECRUITMENT_STATUS: {
      RECRUITING: 'Recrute',
      NOT_RECRUITING: 'Ne Recrute Pas',
    },
  },
  PLAYER_PROFILE: {
    PLAYER_PROFILE: 'Profil',
    INVITES: 'Invitations',
    EDIT_PROFILE: 'Éditer le profil',
    DESCRIPTION: 'Description',
    PRIMARY: 'Principal?',
    SUBMIT: 'Envoyer',
    FRIEND_CODE: 'Code ami',
    FRIEND_CODES: 'Codes Amis',
    ADD_FRIEND_CODE: 'Ajouter un Code Ami',
    AVATAR_URL: 'Avatar URL',
    ABOUT_ME: 'À Propos de moi',
    LANGUAGE: 'Langue',
    THEME: 'Thème',
    TIMEZONE: 'Fuseau Horaire',
    SAVE: 'Enregistrer',
    PLAYER_NOTES: 'Player Notes', // TODO
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
    EN_US: 'Anglais (États-Unis)',
    EN_GB: 'Anglais (Royaume-Uni)',
    DE: 'Allemand',
    ES: 'Espagnol',
    FR: 'Français',
    JA: 'Japonais',
  },
  COLORS: {
    RED_1: 'Rouge 1',
    RED_2: 'Rouge 2',
    RED_3: 'Rouge 3',
    RED_4: 'Rouge 4',
    ORANGE_1: 'Orange 1',
    ORANGE_2: 'Orange 2',
    ORANGE_3: 'Orange 3',
    ORANGE_4: 'Orange 4',
    YELLOW_1: 'Jaune 1',
    YELLOW_2: 'Jaune 2',
    YELLOW_3: 'Jaune 3',
    YELLOW_4: 'Jaune 4',
    GREEN_1: 'Vert 1',
    GREEN_2: 'Vert 2',
    GREEN_3: 'Vert 3',
    GREEN_4: 'Vert 4',
    AQUA_1: 'Turquoise 1',
    AQUA_2: 'Turquoise 2',
    AQUA_3: 'Turquoise 3',
    AQUA_4: 'Turquoise 4',
    BLUE_1: 'Bleu 1',
    BLUE_2: 'Bleu 2',
    BLUE_3: 'Bleu 3',
    BLUE_4: 'Bleu 4',
    INDIGO_1: 'Indigo 1',
    INDIGO_2: 'Indigo 2',
    INDIGO_3: 'Indigo 3',
    INDIGO_4: 'Indigo 4',
    PURPLE_1: 'Purple 1',
    PURPLE_2: 'Purple 2',
    PURPLE_3: 'Purple 3',
    PURPLE_4: 'Purple 4',
    PINK_1: 'Rose 1',
    PINK_2: 'Rose 2',
    PINK_3: 'Rose 3',
    PINK_4: 'Rose 4',
    GREY_1: 'Gris 1',
    GREY_2: 'Gris 2',
    GREY_3: 'Gris 3',
    BLACK: 'Noir',
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
    AF: 'Afghanistan',
    AX: 'Îles Åland',
    AL: 'Albanie',
    DZ: 'Algérie',
    AS: 'Samoa américaines',
    AD: 'Andorre',
    AO: 'Angola',
    AI: 'Anguilla',
    AQ: 'Antarctique',
    AG: 'Antigua-et-Barbuda',
    AR: 'Argentine',
    AM: 'Arménie',
    AW: 'Aruba',
    AU: 'Australie',
    AT: 'Autriche',
    AZ: 'Azerbaïdjan',
    BS: 'Bahamas',
    BH: 'Bahreïn',
    BD: 'Bangladesh',
    BB: 'Barbade',
    BY: 'Biélorussie',
    BE: 'Belgique',
    BZ: 'Belize',
    BJ: 'Bénin',
    BM: 'Bermudes',
    BT: 'Bhoutan',
    BO: 'Bolivie',
    BQ: 'Pays-Bas caribéens',
    BA: 'Bosnie-Herzégovine',
    BW: 'Botswana',
    BV: 'Île Bouvet',
    BR: 'Brésil',
    IO: "Territoire britannique de l'océan Indien",
    BN: 'Brunei',
    BG: 'Bulgarie',
    BF: 'Burkina Faso',
    BI: 'Burundi',
    KH: 'Cambodge',
    CM: 'Cameroun',
    CA: 'Canada',
    CV: 'Cap-Vert',
    KY: 'Îles Caïmans',
    CF: 'République centrafricaine',
    TD: 'Tchad',
    CL: 'Chili',
    CN: 'Chine',
    CX: 'Île Christmas',
    CC: 'Îles Cocos',
    CO: 'Colombie',
    KM: 'Comores',
    CG: 'République du Congo',
    CD: 'République démocratique du Congo',
    CK: 'Îles Cook',
    CR: 'Costa Rica',
    CI: "Côte d'Ivoire",
    HR: 'Croatie',
    CU: 'Cuba',
    CW: 'Curaçao',
    CY: 'Chypre',
    CZ: 'Tchéquie',
    DK: 'Danemark',
    DJ: 'Djibouti',
    DM: 'Dominique',
    DO: 'République dominicaine',
    EC: 'Équateur',
    EG: 'Égypte',
    SV: 'Salvador',
    GQ: 'Guinée équatoriale',
    ER: 'Érythrée',
    EE: 'Estonie',
    ET: 'Éthiopie',
    FK: 'Malouines',
    FO: 'Îles Féroé',
    FJ: 'Fidji',
    FI: 'Finlande',
    FR: 'France',
    GF: 'Guyane',
    PF: 'Polynésie française',
    TF: 'Terres australes et antarctiques françaises',
    GA: 'Gabon',
    GM: 'Gambie',
    GE: 'Géorgie',
    DE: 'Allemagne',
    GH: 'Ghana',
    GI: 'Gibraltar',
    GR: 'Grèce',
    GL: 'Groenland',
    GD: 'Grenade',
    GP: 'Guadeloupe',
    GU: 'Guam',
    GT: 'Guatemala',
    GG: 'Guernesey',
    GN: 'Guinée',
    GW: 'Guinée-Bissau',
    GY: 'Guyana',
    HT: 'Haïti',
    HM: 'Îles Heard-et-MacDonald',
    VA: 'Saint-Siège (État de la Cité du Vatican)',
    HN: 'Honduras',
    HK: 'Hong Kong',
    HU: 'Hongrie',
    IS: 'Islande',
    IN: 'Inde',
    ID: 'Indonésie',
    IR: 'Iran',
    IQ: 'Irak',
    IE: 'Irlande',
    IM: 'Île de Man',
    IL: 'Israël',
    IT: 'Italie',
    JM: 'Jamaïque',
    JP: 'Japon',
    JE: 'Jersey',
    JO: 'Jordanie',
    KZ: 'Kazakhstan',
    KE: 'Kenya',
    KI: 'Kiribati',
    KP: 'Corée du Nord',
    KR: 'Corée du Sud',
    KW: 'Koweït',
    KG: 'Kirghizistan',
    LA: 'Laos',
    LV: 'Lettonie',
    LB: 'Liban',
    LS: 'Lesotho',
    LR: 'Liberia',
    LY: 'Libye',
    LI: 'Liechtenstein',
    LT: 'Lituanie',
    LU: 'Luxembourg',
    MO: 'Macao',
    MK: 'Macédoine du Nord',
    MG: 'Madagascar',
    MW: 'Malawi',
    MY: 'Malaisie',
    MV: 'Maldives',
    ML: 'Mali',
    MT: 'Malte',
    MH: 'Îles Marshall',
    MQ: 'Martinique',
    MR: 'Mauritanie',
    MU: 'Maurice',
    YT: 'Mayotte',
    MX: 'Mexique',
    FM: 'États fédérés de Micronésie',
    MA: 'Maroc',
    MD: 'Moldavie',
    MC: 'Monaco',
    MN: 'Mongolie',
    ME: 'Monténégro',
    MS: 'Montserrat',
    MZ: 'Mozambique',
    MM: 'Birmanie',
    NA: 'Namibie',
    NR: 'Nauru',
    NP: 'Népal',
    NL: 'Pays-Bas',
    NC: 'Nouvelle-Calédonie',
    NZ: 'Nouvelle-Zélande',
    NI: 'Nicaragua',
    NE: 'Niger',
    NG: 'Nigeria',
    NU: 'Niue',
    NF: 'Île Norfolk',
    MP: 'Îles Mariannes du Nord',
    NO: 'Norvège',
    OM: 'Oman',
    PK: 'Pakistan',
    PW: 'Palaos',
    PS: 'Palestine',
    PA: 'Panama',
    PG: 'Papouasie-Nouvelle-Guinée',
    PY: 'Paraguay',
    PE: 'Pérou',
    PH: 'Philippines',
    PN: 'Îles Pitcairn',
    PL: 'Pologne',
    PT: 'Portugal',
    PR: 'Porto Rico',
    QA: 'Qatar',
    RE: 'La Réunion',
    RO: 'Roumanie',
    RU: 'Russie',
    RW: 'Rwanda',
    BL: 'Saint-Barthélemy',
    SH: 'Sainte-Hélène, Ascension et Tristan da Cunha',
    KN: 'Saint-Christophe-et-Niévès',
    LC: 'Sainte-Lucie',
    MF: 'Saint-Martin',
    PM: 'Saint-Pierre-et-Miquelon',
    VC: 'Saint-Vincent-et-les-Grenadines',
    WS: 'Samoa',
    SM: 'Saint-Marin',
    ST: 'Sao Tomé-et-Principe',
    SA: 'Arabie saoudite',
    SN: 'Sénégal',
    RS: 'Serbie',
    SC: 'Seychelles',
    SL: 'Sierra Leone',
    SG: 'Singapour',
    SX: 'Saint-Martin',
    SK: 'Slovaquie',
    SI: 'Slovénie',
    SB: 'Îles Salomon',
    SO: 'Somalie',
    ZA: 'Afrique du Sud',
    GS: 'Géorgie du Sud-et-les îles Sandwich du Sud',
    SS: 'Soudan du Sud',
    ES: 'Espagne',
    LK: 'Sri Lanka',
    SD: 'Soudan',
    SR: 'Suriname',
    SJ: 'Svalbard et île Jan Mayen',
    SZ: 'Eswatini',
    SE: 'Suède',
    CH: 'Suisse',
    SY: 'Syrie',
    TW: 'Taïwan / (République de Chine (Taïwan))',
    TJ: 'Tadjikistan',
    TZ: 'Tanzanie',
    TH: 'Thaïlande',
    TL: 'Timor oriental',
    TG: 'Togo',
    TK: 'Tokelau',
    TO: 'Tonga',
    TT: 'Trinité-et-Tobago',
    TN: 'Tunisie',
    TR: 'Turquie',
    TM: 'Turkménistan',
    TC: 'Îles Turques-et-Caïques',
    TV: 'Tuvalu',
    UG: 'Ouganda',
    UA: 'Ukraine',
    AE: 'Émirats arabes unis',
    GB: 'Royaume-Uni',
    US: 'États-Unis',
    UM: 'Îles mineures éloignées des États-Unis',
    UY: 'Uruguay',
    UZ: 'Ouzbékistan',
    VU: 'Vanuatu',
    VE: 'Venezuela',
    VN: 'Viêt Nam',
    VG: 'Îles Vierges britanniques',
    VI: 'Îles Vierges des États-Unis',
    WF: 'Wallis-et-Futuna',
    EH: 'République arabe sahraouie démocratique',
    YE: 'Yémen',
    ZM: 'Zambie',
    ZW: 'Zimbabwe',
  },
};

export default fr;
