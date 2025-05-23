export type TournamentTemplate = {
  id: number;
  template_name: string;
  name: string;
  game: string;
  mode: string;
  series_id: number | null;
  is_squad: boolean;
  registrations_open: boolean;
  date_start: number;
  date_end: number;
  description: string;
  use_series_description: boolean;
  series_stats_include: boolean;
  logo: string | null;
  use_series_logo: boolean;
  url: string | null;
  registration_deadline: number | null;
  registration_cap: number | null;
  teams_allowed: boolean;
  teams_only: boolean;
  team_members_only: boolean;
  min_squad_size: number | null;
  max_squad_size: number | null;
  squad_tag_required: boolean;
  squad_name_required: boolean;
  mii_name_required: boolean;
  host_status_required: boolean;
  checkins_enabled: boolean;
  checkins_open: boolean;
  min_players_checkin: number | null;
  verification_required: boolean;
  verified_fc_required: boolean;
  is_viewable: boolean;
  is_public: boolean;
  show_on_profiles: boolean;
  require_single_fc: boolean;
  min_representatives: number | null;
  ruleset: string;
  use_series_ruleset: boolean;
  organizer: string;
  location: string;
};
