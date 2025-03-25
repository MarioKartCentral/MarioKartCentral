import type { TournamentBasic } from "$lib/types/tournament";

export type CreateTournament = TournamentBasic & {
  logo_file: string | null;
  remove_logo: boolean;
};
