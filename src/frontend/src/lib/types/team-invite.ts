export type TeamInvite = {
  invite_id: number;
  date: number;
  team_id: number;
  team_name: string;
  team_tag: string;
  team_color: number;
  roster_id: number;
  roster_name: string | null;
  roster_tag: string | null;
  game: string;
  mode: string;
};

type LeaveRoster = {
  team_id: number;
  team_name: string;
  team_tag: string;
  team_color: string;
  roster_id: number;
  roster_name: string | null;
  roster_tag: string | null;
};

export type TeamInviteApproval = TeamInvite & {
  player_id: number;
  player_name: string;
  player_country_code: string;
  roster_leave_id: number | null;
  roster_leave: LeaveRoster | null;
};
