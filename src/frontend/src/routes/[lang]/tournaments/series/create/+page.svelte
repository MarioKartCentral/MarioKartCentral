<script lang="ts">
  import CreateEditTournamentSeriesForm from '$lib/components/tournaments/series/CreateEditTournamentSeriesForm.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
</script>

{#if check_permission(user_info, permissions.create_series)}
  <CreateEditTournamentSeriesForm />
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}
