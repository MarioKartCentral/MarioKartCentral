<script lang="ts">
  import { onMount } from 'svelte';
  import type { TournamentTemplateMinimal } from '$lib/types/tournaments/create/tournament-template-minimal';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';

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

<Section header={$LL.TOURNAMENTS.MANAGE.SELECT_TEMPLATE()}>
  <div slot="header_content">
    {#if series_id}
      <Button href="/{$page.params.lang}/tournaments/series/details?id={series_id}"
        >{$LL.TOURNAMENTS.MANAGE.BACK_TO_SERIES()}</Button
      >
    {/if}
  </div>
  <Table>
    <tr class="row-1">
      <td class="left">
        {#if series_id}
          <a href="/{$page.params.lang}/tournaments/series/create_tournament?id={series_id}"
            >{$LL.TOURNAMENTS.MANAGE.START_FROM_SCRATCH()}</a
          >
        {:else}
          <a href="/{$page.params.lang}/tournaments/create">{$LL.TOURNAMENTS.MANAGE.START_FROM_SCRATCH()}</a>
        {/if}
      </td>
    </tr>
    {#each templates as template, i (template.id)}
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
