type TransferRoster = {
  team_id: number;
  team_name: string;
  team_tag: string;
  team_color: number;
  roster_id: number;
  roster_name: string | null;
  roster_tag: string | null;
};

export type TeamTransfer = {
  invite_id: number;
  date: number;
  player_id: number;
  player_name: string;
  player_country_code: string;
  game: string;
  mode: string;
  roster_leave: TransferRoster | null;
  roster_join: TransferRoster | null;
};
