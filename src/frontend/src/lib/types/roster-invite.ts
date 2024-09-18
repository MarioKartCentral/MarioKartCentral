import type { FriendCode } from './friend-code';
import type { Discord } from './discord';

export type RosterInvite = {
  player_id: number;
  name: string;
  country_code: string;
  is_banned: boolean;
  discord: Discord | null;
  invite_date: number;
  friend_codes: FriendCode[];
};
