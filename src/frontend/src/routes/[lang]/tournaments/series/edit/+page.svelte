<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentSeriesForm from '$lib/components/tournaments/series/CreateEditTournamentSeriesForm.svelte';
  import { onMount } from 'svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let series_id: number | null;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    series_id = param_id ? Number(param_id) : null;
  });
</script>

{#if series_id}
  {#if check_series_permission(user_info, series_permissions.edit_series, series_id)}
    <CreateEditTournamentSeriesForm {series_id} is_edit={true} />
  {:else}
    {$LL.NO_PERMISSION()}
  {/if}
{/if}
