import type { RosterBasic } from './roster-basic';

export type TeamTransfer = {
  invite_id: number;
  date: number;
  is_bagger_clause: boolean;
  player_id: number;
  player_name: string;
  player_country_code: string;
  game: string;
  mode: string;
  roster_leave: RosterBasic | null;
  roster_join: RosterBasic | null;
};

export type TransferList = {
  transfers: TeamTransfer[];
  transfer_count: number;
  page_count: number;
};
