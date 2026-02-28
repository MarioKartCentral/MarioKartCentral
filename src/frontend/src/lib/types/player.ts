import type { Discord } from './discord';

export type PlayerBasic = {
  id: number;
  name: string;
  country_code: string;
  is_banned: boolean;
  is_verified: boolean;
};

export type Player = PlayerBasic & {
  is_hidden: boolean;
  is_shadow: boolean;
  join_date: number;
  discord: Discord | null;
};
