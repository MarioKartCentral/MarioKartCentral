import type { TournamentSquad } from '../tournament-squad';
import type { TournamentPlayer } from '../tournament-player';

export type RegistrationDetails = {
  squad: TournamentSquad;
  player: TournamentPlayer | null;
  is_squad_captain: boolean;
  is_invite: boolean;
};

export type MyTournamentRegistration = {
  player_id: number;
  tournament_id: number;
  registrations: RegistrationDetails[];
};
