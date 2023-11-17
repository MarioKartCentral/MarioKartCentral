<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';

  export let series_id: number | null;
  export let permission: string;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  $: series_perms = user_info.series_permissions.find((s) => s.series_id === series_id);
</script>

{#if (series_perms && series_perms.permissions.includes(permission)) || user_info.permissions.includes(permission)}
  <slot />
{/if}
