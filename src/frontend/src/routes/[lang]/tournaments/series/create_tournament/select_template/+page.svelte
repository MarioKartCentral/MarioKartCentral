<script lang="ts">
  import TemplateSelector from '$lib/components/tournaments/create/TemplateSelector.svelte';
  import { page } from '$app/stores';

  let id = 0;

  let param_id = $page.url.searchParams.get('id');
  id = Number(param_id);
</script>

<TemplateSelector series_id={id} />
