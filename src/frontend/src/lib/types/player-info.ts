import type { FriendCode } from '$lib/types/friend-code';
import type { BanInfoBasic } from '$lib/types/ban-info';
import type { UserSettings } from '$lib/types/user-settings';
import type { PlayerRoster } from './player-roster';
import type { Discord } from './discord';
import type { Player } from './player';
import type { Role } from './role';

type PlayerNameChange = {
  id: number;
  name: string;
  date: number;
  approval_status: string;
};

export type PlayerNotes = {
  notes: string;
  edited_by: Player | null;
  date: number;
};

export type PlayerInfo = {
  id: number;
  name: string;
  country_code: string | null;
  is_hidden: boolean;
  is_shadow: boolean;
  is_banned: boolean;
  discord: Discord | null;
  friend_codes: FriendCode[];
  join_date: number;
  rosters: PlayerRoster[];
  ban_info: BanInfoBasic | null;
  user_settings: UserSettings | null;
  name_changes: PlayerNameChange[];
  notes: PlayerNotes | null;
  roles: Role[];
};

export type PlayerList = {
  player_list: PlayerInfo[];
  player_count: number;
  page_count: number;
};
