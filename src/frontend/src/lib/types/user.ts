import type { Player } from './player';

export type User = {
  id: number;
  email: string;
  join_date: number;
  player: Player | null;
};
