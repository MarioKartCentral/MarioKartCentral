<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { series_permissions, setSeriesPerms, addPermission, permissions } from '$lib/util/util';
  import SeriesPermissionCheck from '$lib/components/common/SeriesPermissionCheck.svelte';

  addPermission(permissions.create_tournament);
  setSeriesPerms();

  let param_temp_id = $page.url.searchParams.get('template_id');
  let template_id = param_temp_id ? Number(param_temp_id) : null;

  let param_id = $page.url.searchParams.get('id');
  let id = Number(param_id);
</script>

<SeriesPermissionCheck series_id={id} permission={series_permissions.create_tournament}>
  <CreateEditTournamentForm {template_id} series_restrict={true} />
</SeriesPermissionCheck>
