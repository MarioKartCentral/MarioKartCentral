import type { PlayerBasic } from './player';

export type PlayerNameChangeRequest = {
  id: number;
  player_id: number;
  player_country: string;
  old_name: string;
  new_name: string;
  date: number;
  approval_status: string;
  handled_by: PlayerBasic | null;
};

export type PlayerNameChangeRequestList = {
  change_list: PlayerNameChangeRequest[];
  count: number;
  page_count: number;
};
