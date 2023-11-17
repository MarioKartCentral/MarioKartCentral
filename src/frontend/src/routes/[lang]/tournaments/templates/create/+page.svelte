<script lang="ts">
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { permissions, addPermission } from '$lib/util/util';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import { page } from '$app/stores';

  addPermission(permissions.create_tournament_template);

  let param_temp_id = $page.url.searchParams.get('template_id');
  let template_id = param_temp_id ? Number(param_temp_id) : null;
</script>

<PermissionCheck permission={permissions.create_tournament_template}>
  <CreateEditTemplateForm {template_id} />
</PermissionCheck>
