<script lang="ts">
  import { permissions, addPermission } from '$lib/util/util';
  import PermissionCheck from '$lib/components/common/PermissionCheck.svelte';
  import { page } from '$app/stores';
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { onMount } from 'svelte';

  addPermission(permissions.edit_tournament_template);

  let template_id: number | null;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('id');
    template_id = param_temp_id ? Number(param_temp_id) : null;
  });
</script>

<PermissionCheck permission={permissions.edit_tournament_template}>
  {#if template_id}
    <CreateEditTemplateForm {template_id} is_edit={true} />
  {/if}
</PermissionCheck>
