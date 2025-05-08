import type { Player } from './player';
import type { APIToken } from './api-tokens';

export type User = {
  id: number;
  email: string;
  join_date: number;
  email_confirmed: boolean;
  force_password_reset: boolean;
  player: Player | null;
};

export type UserDetailed = User & {
  tokens: APIToken[];
};
