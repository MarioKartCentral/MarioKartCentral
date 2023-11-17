<script lang="ts">
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { permissions, addPermission, setSeriesPerms } from '$lib/util/util';
  import { page } from '$app/stores';

  addPermission(permissions.create_tournament_template);
  setSeriesPerms();

  let param_temp_id = $page.url.searchParams.get('template_id');
  let template_id = param_temp_id ? Number(param_temp_id) : null;

  let param_series_id = $page.url.searchParams.get('series_id');
  let series_id = param_series_id ? Number(param_series_id) : null;
</script>

<CreateEditTemplateForm {template_id} {series_id} series_restrict={true} />
