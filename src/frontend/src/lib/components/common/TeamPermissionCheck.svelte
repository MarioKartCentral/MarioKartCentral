<script lang="ts">
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
  
    export let team_id: number;
    export let permission: string;
  
    let user_info: UserInfo;
    user.subscribe((value) => {
      user_info = value;
    });

    $: team_perms = user_info.team_permissions.find(t => t.team_id === team_id);
</script>

{#if team_perms && team_perms.permissions.includes(permission)}
    <slot/>
{/if}