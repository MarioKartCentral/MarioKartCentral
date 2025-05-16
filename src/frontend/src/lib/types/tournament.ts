import type { TournamentPlacement } from "./tournament-placement";

export type TournamentBasic = {
  name: string;
  series_id: number | null;
  date_start: number;
  date_end: number;
  logo: string | null;
  use_series_logo: boolean;
  url: string | null;
  organizer: string;
  location: string | null;
  game: string;
  mode: string;
  is_squad: boolean;
  min_squad_size: number | null;
  max_squad_size: number | null;
  squad_tag_required: boolean;
  squad_name_required: boolean;
  teams_allowed: boolean;
  teams_only: boolean;
  team_members_only: boolean;
  min_representatives: number | null;
  host_status_required: boolean;
  mii_name_required: boolean;
  require_single_fc: boolean;
  checkins_enabled: boolean;
  checkins_open: boolean;
  min_players_checkin: number | null;
  verification_required: boolean;
  use_series_description: boolean;
  description: string;
  use_series_ruleset: boolean;
  ruleset: string;
  registrations_open: boolean;
  registration_cap: number | null;
  registration_deadline: number | null;
  is_viewable: boolean;
  is_public: boolean;
  is_deleted: boolean;
  show_on_profiles: boolean;
  series_stats_include: boolean;
  verified_fc_required: boolean;
  bagger_clause_enabled: boolean;
};

export type Tournament = {
  id: number;
  series_name: string | null;
  series_url: string | null;
  series_description: string | null;
  series_ruleset: string | null;
} & TournamentBasic;

export type TournamentWithPlacements = Tournament & {
  placements: TournamentPlacement[];
}

export enum StatsMode {
  TEAM_MEDALS = 'team_medals',
  TEAM_APPEARANCES = 'team_appearances',
  PLAYER_MEDALS = 'player_medals',
  PLAYER_APPEARANCES = 'player_appearances',
}
