import type { PlayerInfo } from '$lib/types/player-info';

export type UserInfo = {
  id: number | null;
  player_id: number | null;
  player: PlayerInfo | null;
  is_checked: boolean;
};
