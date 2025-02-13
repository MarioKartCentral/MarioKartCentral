import type { PlayerBasic } from './player';
import type { FriendCode } from './friend-code';

export type FriendCodeEdit = {
  id: number;
  old_fc: string | null;
  new_fc: string | null;
  is_active: boolean | null;
  date: number;
  fc: FriendCode;
  player: PlayerBasic;
  handled_by: PlayerBasic | null;
};

export type FriendCodeEditList = {
  change_list: FriendCodeEdit[];
  count: number;
  page_count: number;
};
