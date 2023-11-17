<script lang="ts">
  import { permissions, addPermission, setSeriesPerms } from '$lib/util/util';

  import { page } from '$app/stores';
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';

  setSeriesPerms();
  addPermission(permissions.edit_tournament_template);

  let param_temp_id = $page.url.searchParams.get('id');
  let template_id = param_temp_id ? Number(param_temp_id) : null;
</script>

{#if template_id}
  <CreateEditTemplateForm {template_id} is_edit={true} series_restrict={true} />
{/if}
