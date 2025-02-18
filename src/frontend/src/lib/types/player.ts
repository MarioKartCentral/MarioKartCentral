import type { Discord } from './discord';

export type PlayerBasic = {
  id: number;
  name: string;
  country_code: string;
};

export type Player = PlayerBasic & {
  is_hidden: boolean;
  is_shadow: boolean;
  is_banned: boolean;
  join_date: number;
  discord: Discord | null;
};
