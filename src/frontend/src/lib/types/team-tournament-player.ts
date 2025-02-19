import type { RosterPlayer } from './roster-player';

export type TeamTournamentPlayer = RosterPlayer & {
  is_captain: boolean;
  is_representative: boolean;
  is_bagger_clause: boolean;
};
