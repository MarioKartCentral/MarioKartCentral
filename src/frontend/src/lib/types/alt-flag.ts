import type { PlayerBasic } from './player';

export type AltFlag = {
  id: number;
  type: string;
  data: string;
  score: number;
  date: number;
  fingerprint_hash: string | null;
  players: PlayerBasic[];
};

export type AltFlagList = {
  flags: AltFlag[];
  count: number;
  page_count: number;
};
