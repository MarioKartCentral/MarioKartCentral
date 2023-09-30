import type { FriendCode } from './friend-code';

export type RosterPlayer = {
  player_id: number;
  name: string;
  country_code: string;
  is_banned: boolean;
  discord_id: string;
  join_date: number;
  friend_codes: FriendCode[];
};
