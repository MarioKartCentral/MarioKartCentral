export type PlayerTransferItem = {
  team_id: number;
  team_name: string;
  roster_id: number;
  roster_name: string | null;
  roster_lead_id: number | null;
  join_date: number;
  leave_date: number | null;
  is_accepted: boolean;
  is_bagger_clause: boolean;
}

export type PlayerTransferHistory = {
  history: PlayerTransferItem[] | null;
}

