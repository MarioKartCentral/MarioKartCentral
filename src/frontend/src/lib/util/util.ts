import { getContext } from 'svelte';

export function addPermission(permission: string) {
    let ctx: any = getContext('page-init');
    ctx.addPermission(permission);
}