export type TeamEditRequest = {
  id: number;
  team_id: number;
  old_name: string | null;
  old_tag: string | null;
  new_name: string | null;
  new_tag: string | null;
  date: number;
  approval_status: string;
};
