import type { PlayerBasic } from "./player";

export type TeamEditRequest = {
  id: number;
  team_id: number;
  old_name: string;
  old_tag: string;
  new_name: string;
  new_tag: string;
  color: number;
  date: number;
  approval_status: string;
  handled_by: PlayerBasic | null;
};

export type TeamEditList = {
  change_list: TeamEditRequest[];
  count: number;
  page_count: number;
}