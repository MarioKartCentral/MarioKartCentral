import type { Permission } from "$lib/types/permission";
import type { Player } from "$lib/types/player";

export type Role = {
    id: number;
    name: string;
    position: number;
}

export type RoleInfo = Role & {
    permissions: Permission[];
    players: Player[];
}