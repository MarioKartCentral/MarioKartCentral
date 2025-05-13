import type { PlayerBasic } from './player';

export type IPAddress = {
  id: number;
  ip_address: string | null;
  is_mobile: boolean;
  is_vpn: boolean;
  country: string | null;
  city: string | null;
  region: string | null;
  asn: string | null;
};

export type IPAddressWithUserCount = IPAddress & {
  user_count: number;
};

export type IPAddressList = {
  ip_addresses: IPAddressWithUserCount[];
  count: number;
  page_count: number;
};

export type UserIPTimeRange = {
  id: number;
  user_id: number;
  ip_address: IPAddress;
  date_earliest: number;
  date_latest: number;
  times: number;
};

export type PlayerIPTimeRange = {
  time_range: UserIPTimeRange;
  player: PlayerBasic | null;
};

export type PlayerIPHistory = {
  player_id: number;
  ips: UserIPTimeRange[];
};

export type IPHistory = {
  ip_id: number;
  history: PlayerIPTimeRange[];
};
