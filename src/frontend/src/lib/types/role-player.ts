import type { Player } from "$lib/types/player";

export type RolePlayer = Player & {
    expires_on: number | null;
}