export type BanInfo = {
  player_id: number;
  banned_by: number;
  ban_date: number;
  is_indefinite: boolean;
  expiration_date: number;
  reason: string;
};
