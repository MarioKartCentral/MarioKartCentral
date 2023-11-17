<script lang="ts">
  import { onMount } from 'svelte';
  import type { TournamentTemplateMinimal } from '$lib/types/tournaments/create/tournament-template-minimal';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import LinkButton from '$lib/components/common/LinkButton.svelte';

  export let series_id: number | null = null;

  let templates: TournamentTemplateMinimal[] = [];

  onMount(async () => {
    const series_var = series_id ? `?series_id=${series_id}` : '';
    const res = await fetch(`/api/tournaments/templates/list${series_var}`);
    if (res.status === 200) {
      const body = await res.json();
      for (let t of body) {
        templates.push(t);
      }
      templates = templates;
    }
  });
</script>

<Section header="Select Template">
  <div slot="header_content">
    {#if series_id}
      <LinkButton href="/{$page.params.lang}/tournaments/series/details?id={series_id}">Back to Series</LinkButton>
    {/if}
  </div>
  <Table>
    {#if !series_id}
      <tr class="row-1">
        <td class="left">
          <a href="/{$page.params.lang}/tournaments/create">Start from scratch</a>
        </td>
      </tr>
    {/if}
    {#each templates as template, i}
      <tr class="row-{i % 2}">
        <td class="left">
          {#if series_id}
            <a href="/{$page.params.lang}/tournaments/series/create_tournament?id={series_id}&template_id={template.id}"
              >{template.template_name}</a
            >
          {:else}
            <a href="/{$page.params.lang}/tournaments/create?template_id={template.id}">{template.template_name}</a>
          {/if}
        </td>
      </tr>
    {/each}
  </Table>
</Section>

<style>
  td.left {
    text-align: left;
  }
</style>
