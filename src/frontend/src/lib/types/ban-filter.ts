export type BanFilter = {
    player_id: number | null;
    banned_by: number | null;
    is_indefinite: boolean | null;
    expires_before: number | null;
    expires_after: number | null;
    banned_before: number | null;
    banned_after: number | null;
    reason: string | null;
    page: number | null;
};

export type BanHistoricalFilter = BanFilter & {
    unbanned_by: number | null;
    unbanned_before: number | null;
    unbanned_after: number | null;
};
  
  