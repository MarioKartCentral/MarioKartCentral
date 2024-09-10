<script lang="ts">
  import { onMount } from 'svelte';
  import type { TournamentTemplateMinimal } from '$lib/types/tournaments/create/tournament-template-minimal';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';

  import Button from '$lib/components/common/buttons/Button.svelte';

  export let series_id: number | null = null;

  let templates: TournamentTemplateMinimal[] = [];

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

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

<Section header="Templates">
  <div slot="header_content">
    {#if check_series_permission(user_info, series_permissions.create_tournament_template, series_id)}
      {#if series_id}
        <Button href="/{$page.params.lang}/tournaments/series/create_template?series_id={series_id}"
          >Create Template</Button
        >
      {:else}
        <Button href="/{$page.params.lang}/tournaments/templates/create">Create Template</Button>
      {/if}
    {/if}
    {#if series_id}
      <Button href="/{$page.params.lang}/tournaments/series/details?id={series_id}">Back to Series</Button>
    {/if}
  </div>
  <Table>
    {#each templates as template, i}
      <tr class="row-{i % 2}">
        <td class="left">
          <a href="/{$page.params.lang}/tournaments/create?template_id={template.id}">{template.template_name}</a>
        </td>
        <td>
          <div class="settings">
            {#if check_series_permission(user_info, series_permissions.edit_tournament_template, series_id)}
              <Button href="/{$page.params.lang}/tournaments/templates/edit?id={template.id}">Edit</Button>
            {/if}
            {#if check_series_permission(user_info, series_permissions.create_tournament_template, series_id)}
              {#if series_id}
                <Button
                  href="/{$page.params
                    .lang}/tournaments/series/create_template?series_id={series_id}&template_id={template.id}"
                  >Duplicate</Button
                >
              {:else}
                <Button href="/{$page.params.lang}/tournaments/templates/create?template_id={template.id}"
                  >Duplicate</Button
                >
              {/if}
            {/if}
            <div>Delete</div>
          </div>
        </td>
      </tr>
    {/each}
  </Table>
</Section>

<style>
  td div {
    display: inline-block;
    margin: 0 10px;
  }
  .left {
    text-align: left;
  }
  .settings {
    float: right;
  }
  .settings div {
    padding: 0 5px;
  }
</style>
