import type { FriendCode } from '$lib/types/friend-code';
import type { BanInfo } from '$lib/types/ban-info';
import type { UserSettings } from '$lib/types/user-settings';
import type { PlayerRoster } from './player-roster';

export type PlayerInfo = {
  id: number;
  name: string;
  country_code: string | null;
  is_hidden: boolean;
  is_shadow: boolean;
  is_banned: boolean;
  discord_id: string | null;
  friend_codes: FriendCode[];
  rosters: PlayerRoster[];
  ban_info: BanInfo | null;
  user_settings: UserSettings | null;
};
