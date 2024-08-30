import type { FriendCode } from "./friend-code";

export type TournamentPlayer = {
  id: number;
  player_id: number;
  squad_id: number | null;
  timestamp: number;
  is_checked_in: boolean;
  mii_name: string | null;
  can_host: boolean;
  name: string;
  country_code: string | null;
  discord_id: string | null;
  selected_fc_id: number | null;
  friend_codes: FriendCode[];
  is_squad_captain: boolean;
  is_representative: boolean;
  is_invite: boolean;
};
