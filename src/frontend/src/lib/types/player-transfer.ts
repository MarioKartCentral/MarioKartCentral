export type PlayerTransferItem = {
  id: number;
  team_id: number;
  team_name: string;
  game: string;
  mode: string;
  join_date: number;
  leave_date: number | null;
  is_bagger_clause: boolean;
  roster_name: string | null;
  is_hidden: boolean;
};

export type PlayerTransferHistory = {
  history: PlayerTransferItem[] | null;
};
