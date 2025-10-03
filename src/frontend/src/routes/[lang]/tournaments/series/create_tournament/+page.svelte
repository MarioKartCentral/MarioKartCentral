<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let template_id: number | null;
  let id: number;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('template_id');
    template_id = param_temp_id ? Number(param_temp_id) : null;

    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
  });
</script>

{#if id}
  {#if check_series_permission(user_info, series_permissions.create_tournament, id)}
    <CreateEditTournamentForm {template_id} series_restrict={true} series_id={id} />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
