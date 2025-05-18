import type { PlayerBasic } from './player';

export type AltFlagUser = {
  user_id: number;
  player: PlayerBasic | null;
};

export type AltFlag = {
  id: number;
  type: string;
  flag_key: string;
  data: string;
  score: number;
  date: number;
  fingerprint_hash: string | null;
  users: AltFlagUser[];
};

export type AltFlagList = {
  flags: AltFlag[];
  count: number;
  page_count: number;
};
