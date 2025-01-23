import type { Discord } from './discord';

export type Player = {
  id: number;
  name: string;
  country_code: string | null;
  is_hidden: boolean;
  is_shadow: boolean;
  is_banned: boolean;
  join_date: number;
  discord: Discord | null;
};
