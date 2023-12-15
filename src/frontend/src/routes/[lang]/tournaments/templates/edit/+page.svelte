<script lang="ts">
  import { permissions, addPermission, setSeriesPerms } from '$lib/util/util';
  import { page } from '$app/stores';
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { onMount } from 'svelte';

  setSeriesPerms();
  addPermission(permissions.edit_tournament_template);

  let template_id: number;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('id');
    template_id = Number(param_temp_id);
  });
</script>

{#if template_id}
  <CreateEditTemplateForm {template_id} is_edit={true} series_restrict={true} />
{/if}
