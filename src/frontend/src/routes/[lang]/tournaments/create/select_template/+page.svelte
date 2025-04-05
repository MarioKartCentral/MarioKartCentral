<script lang="ts">
  import TemplateSelector from '$lib/components/tournaments/create/TemplateSelector.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, series_permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });
</script>

{#if user_info.is_checked}
  {#if check_permission(user_info, series_permissions.create_tournament_template)}
    <TemplateSelector />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}

