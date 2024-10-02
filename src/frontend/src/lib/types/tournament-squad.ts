import type { TournamentPlayer } from '$lib/types/tournament-player';

export type TournamentSquad = {
  id: number;
  name: string | null;
  tag: string | null;
  color: number;
  timestamp: number;
  is_registered: boolean;
  is_approved: boolean;
  players: TournamentPlayer[];
};
