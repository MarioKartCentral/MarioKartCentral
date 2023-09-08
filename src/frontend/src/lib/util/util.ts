import { getContext } from 'svelte';

export function addPermission(permission: string) {
    const ctx: any = getContext('page-init');
    ctx.addPermission(permission);
}