<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { check_permission, series_permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let template_id: number | null;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('template_id');
    template_id = param_temp_id ? Number(param_temp_id) : null;
  });
</script>

{#if check_permission(user_info, series_permissions.create_tournament)}
  <CreateEditTournamentForm {template_id} />
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}
