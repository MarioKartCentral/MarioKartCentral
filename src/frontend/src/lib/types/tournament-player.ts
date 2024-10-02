import type { FriendCode } from './friend-code';
import type { Discord } from './discord';

export type TournamentPlayer = {
  id: number;
  player_id: number;
  squad_id: number | null;
  timestamp: number;
  is_checked_in: boolean;
  is_approved: boolean;
  mii_name: string | null;
  can_host: boolean;
  name: string;
  country_code: string | null;
  discord: Discord | null;
  selected_fc_id: number | null;
  friend_codes: FriendCode[];
  is_squad_captain: boolean;
  is_representative: boolean;
  is_invite: boolean;
  is_bagger_clause: boolean;
};
