export type RosterEditRequest = {
  id: number;
  roster_id: number;
  team_id: number;
  team_name: string;
  team_tag: string;
  old_name: string | null;
  old_tag: string | null;
  new_name: string | null;
  new_tag: string | null;
  color: number;
  date: number;
  approval_status: string;
};
