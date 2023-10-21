import type { FriendCode } from './friend-code';

export type RosterInvite = {
  player_id: number;
  name: string;
  country_code: string;
  is_banned: boolean;
  discord_id: string;
  invite_date: number;
  friend_codes: FriendCode[];
};
