import type { PlayerBasic } from "./player";

export type PlayerClaim = {
  id: number;
  date: number;
  approval_status: string;
  player: PlayerBasic;
  claimed_player: PlayerBasic;
};
