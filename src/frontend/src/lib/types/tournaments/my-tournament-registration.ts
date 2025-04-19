import type { TournamentSquad } from '../tournament-squad';
import type { TournamentPlayer } from '../tournament-player';

export type RegistrationDetails = {
  squad: TournamentSquad;
  player: TournamentPlayer;
};

export type MyTournamentRegistration = {
  player_id: number;
  tournament_id: number;
  registrations: RegistrationDetails[];
};
