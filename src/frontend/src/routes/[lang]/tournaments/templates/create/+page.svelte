<script lang="ts">
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  let template_id: number | null;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('template_id');
    template_id = param_temp_id ? Number(param_temp_id) : null;
  });
</script>

<CreateEditTemplateForm {template_id} />
