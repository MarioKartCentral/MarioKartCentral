export type PlayerTransferItem = {
  team_id: number;
  team_name: string;
  game: string;
  mode: string;
  join_date: number;
  leave_date: number | null;
  roster_name: string | null;
}

export type PlayerTransferHistory = {
  history: PlayerTransferItem[] | null;
}

