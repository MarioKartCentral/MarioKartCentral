import type { TournamentSquad } from '../tournament-squad';
import type { TournamentPlayer } from '../tournament-player';

export type MyTournamentRegistration = {
  player_id: number;
  tournament_id: number;
  squads: TournamentSquad[];
  player: TournamentPlayer | null;
};
