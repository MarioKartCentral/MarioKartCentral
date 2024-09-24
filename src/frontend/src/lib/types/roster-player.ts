import type { FriendCode } from './friend-code';
import type { Discord } from './discord';

export type RosterPlayer = {
  player_id: number;
  name: string;
  country_code: string;
  is_banned: boolean;
  discord: Discord | null;
  join_date: number;
  is_manager: boolean;
  is_leader: boolean;
  is_bagger_clause: boolean;
  friend_codes: FriendCode[];
};
