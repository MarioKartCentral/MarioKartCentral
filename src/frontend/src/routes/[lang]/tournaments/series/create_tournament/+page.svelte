<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { series_permissions, setSeriesPerms, addPermission, permissions } from '$lib/util/util';
  import SeriesPermissionCheck from '$lib/components/common/SeriesPermissionCheck.svelte';
  import { onMount } from 'svelte';

  addPermission(permissions.create_tournament);
  setSeriesPerms();

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
  <SeriesPermissionCheck series_id={id} permission={series_permissions.create_tournament}>
    <CreateEditTournamentForm {template_id} series_restrict={true} />
  </SeriesPermissionCheck>
{/if}
