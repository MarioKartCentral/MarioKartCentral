export type BanInfo = {
  player_id: number;
  banned_by: number;
  ban_date: number;
  is_indefinite: boolean;
  expiration_date: number;
  reason: string;
};

export type BanInfoDetailed = {
  player_name: string
  player_id: number
  player_country_code: string
  is_indefinite: boolean
  ban_date: number
  expiration_date: number
  reason: string
  banned_by_uid: number
  banned_by_pid: number
  banned_by_name: string | null
  unban_date: number | null
  unbanned_by_uid: number | null
  unbanned_by_pid: number | null
  unbanned_by_name: string | null
}

export type HistoricalBanInfo = BanInfo & {
  unbanned_by: number;
};

export type BanListData = {
  ban_list: BanInfoDetailed[]
  ban_count: number
  page_count: number
}
