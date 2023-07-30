import type { FriendCode } from '$lib/types/friend-code';
import type { BanInfo } from '$lib/types/ban-info';
import type { UserSettings } from '$lib/types/user-settings';

export type PlayerInfo = {
  id: number;
  name: string;
  country_code: string | null;
  is_hidden: boolean;
  is_shadow: boolean;
  is_banned: boolean;
  discord_id: string | null;
  friend_codes: FriendCode[];
  ban_info: BanInfo | null;
  user_settings: UserSettings | null;
};
