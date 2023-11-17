import type { CreateTournament } from "./tournaments/create/create-tournament";

export type Tournament = {
  id: number;
  series_name: string | null;
  series_url: string | null;
  series_description: string | null;
  series_ruleset: string | null;
} & CreateTournament;
