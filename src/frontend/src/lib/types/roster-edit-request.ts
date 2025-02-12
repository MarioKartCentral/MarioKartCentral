import type { PlayerBasic } from "./player";

export type RosterEditRequest = {
  id: number;
  roster_id: number;
  team_id: number;
  old_name: string | null;
  old_tag: string | null;
  new_name: string | null;
  new_tag: string | null;
  color: number;
  date: number;
  approval_status: string;
  handled_by: PlayerBasic | null;
};

export type RosterEditList = {
  change_list: RosterEditRequest[];
  count: number;
  page_count: number;
}