import type { Player } from './player';

export type User = {
  id: number;
  email: string;
  join_date: number;
  email_confirmed: boolean;
  force_password_reset: boolean;
  player: Player | null;
};
