<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTournamentForm from '$lib/components/tournaments/CreateEditTournamentForm.svelte';
  import { permissions, addPermission } from '$lib/util/util';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import { onMount } from 'svelte';

  addPermission(permissions.create_tournament);

  let template_id: number | null;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('template_id');
    template_id = param_temp_id ? Number(param_temp_id) : null;
  });
</script>

<PermissionCheck permission={permissions.create_tournament}>
  <CreateEditTournamentForm {template_id} />
</PermissionCheck>
