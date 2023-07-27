export type TournamentPlayer = {
  player_id: number;
  timestamp: number;
  is_checked_in: boolean;
  mii_name: string | null;
  can_host: boolean;
  name: string;
  country_code: string | null;
  discord_id: string | null;
  friend_codes: string[];
};

type PlayerSquadInfo = {
  is_squad_captain: boolean;
  is_invite: boolean;
};

export type SquadPlayer = TournamentPlayer & PlayerSquadInfo;
