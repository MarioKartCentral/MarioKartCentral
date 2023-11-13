import type { CreateTournament } from "../create/create-tournament";

export type CreateTemplate = {
    template_name: string;
} & CreateTournament;