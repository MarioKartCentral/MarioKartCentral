<script lang="ts">
  import TemplateSelector from '$lib/components/tournaments/create/TemplateSelector.svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  let id: number;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
  });
</script>

{#if id}
  <TemplateSelector series_id={id} />
{/if}
