<script lang="ts">
  import TemplateList from '$lib/components/tournaments/templates/TemplateList.svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  let id: number;

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
  });
</script>

{#if id}
  <TemplateList series_id={id} />
{/if}
