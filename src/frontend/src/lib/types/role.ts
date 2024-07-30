import type { Permission } from "$lib/types/permission";
import type { RolePlayer } from "$lib/types/role-player";

export type Role = {
    id: number;
    name: string;
    position: number;
}

export type RoleInfo = Role & {
    permissions: Permission[];
    players: RolePlayer[];
}