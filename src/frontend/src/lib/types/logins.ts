import type { IPAddress } from './ip-addresses';

export type UserLogin = {
  id: number;
  user_id: number;
  fingerprint: string;
  had_persistent_session: boolean;
  date: number;
  logout_date: number | null;
  ip_address: IPAddress;
};

export type PlayerUserLogins = {
  player_id: number;
  logins: UserLogin[];
};
