export type UserAccountInfo = {
  id: number;
  player_id: number | null;
  email_confirmed: boolean;
  force_password_reset: boolean;
};
