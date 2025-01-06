import type { PlayerBasic } from './player-basic';

export type SessionMatchUser = {
  user_id: number;
  date_earliest: number;
  date_latest: number;
  player_info: PlayerBasic;
  is_banned: boolean;
};

export type SessionMatch = {
  date: number;
  users: SessionMatchUser[];
};

export type SessionMatchList = {
  session_matches: SessionMatch[];
  match_count: number;
  page_count: number;
};

export type IPMatchUser = {
  user_id: number;
  date_earliest: number;
  date_latest: number;
  times: number;
  player_info: PlayerBasic;
  is_banned: boolean;
};

export type IPMatch = {
  ip_address: string | null;
  date: number;
  users: IPMatchUser[];
};

export type IPMatchList = {
  ip_matches: IPMatch[];
  match_count: number;
  page_count: number;
};
