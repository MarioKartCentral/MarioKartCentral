import type { PlayerBasic } from './player-basic';

export type PlayerClaim = {
  id: number;
  date: number;
  approval_status: string;
  player: PlayerBasic;
  claimed_player: PlayerBasic;
};
