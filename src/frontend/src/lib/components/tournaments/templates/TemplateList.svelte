<script lang="ts">
    import { onMount } from "svelte";
    import type { TournamentTemplateMinimal } from "$lib/types/tournaments/create/tournament-template-minimal";
    import Section from "$lib/components/common/Section.svelte";
    import Table from "$lib/components/common/Table.svelte";
    import { page } from "$app/stores";
    import { permissions, addPermission, series_permissions } from "$lib/util/util";
    import PermissionCheck from "$lib/components/common/PermissionCheck.svelte";
    import SeriesPermissionCheck from "$lib/components/common/SeriesPermissionCheck.svelte";
    import LinkButton from "$lib/components/common/LinkButton.svelte";

    export let series_id: number | null = null;

    let templates: TournamentTemplateMinimal[] = [];
    addPermission(permissions.create_tournament_template);
    addPermission(permissions.edit_tournament_template);

    onMount(async() => {
        const series_var = series_id ? `?series_id=${series_id}` : '';
        const res = await fetch(`/api/tournaments/templates/list${series_var}`);
        if(res.status === 200) {
            const body = await res.json();
            for(let t of body) {
                templates.push(t);
            }
            templates = templates;
        }
    })
</script>

<Section header="Templates">
    <div slot="header_content">
        <SeriesPermissionCheck series_id={series_id} permission={series_permissions.create_tournament_template}>
            {#if series_id}
                <LinkButton href="/{$page.params.lang}/tournaments/series/create_template?series_id={series_id}">Create Template</LinkButton>
            {:else}
                <LinkButton href="/{$page.params.lang}/tournaments/templates/create">Create Template</LinkButton>
            {/if}
        </SeriesPermissionCheck>
        {#if series_id}
            <LinkButton href="/{$page.params.lang}/tournaments/series/details?id={series_id}">Back to Series</LinkButton>
        {/if}
    </div>
    <Table>
        {#each templates as template, i}
            <tr class="row-{i%2}">
                <td class="left">
                    <a href="/{$page.params.lang}/tournaments/create?template_id={template.id}">{template.template_name}</a>
                </td>
                <td>
                    <div class="settings">
                        <SeriesPermissionCheck series_id={series_id} permission={series_permissions.edit_tournament_template}>
                            <LinkButton href="/{$page.params.lang}/tournaments/templates/edit?id={template.id}">Edit</LinkButton>
                        </SeriesPermissionCheck>
                        <SeriesPermissionCheck series_id={series_id} permission={series_permissions.create_tournament_template}>
                            {#if series_id}
                                <LinkButton href="/{$page.params.lang}/tournaments/series/create_template?series_id={series_id}&template_id={template.id}">Duplicate</LinkButton>
                            {:else}
                                <LinkButton href="/{$page.params.lang}/tournaments/templates/create?template_id={template.id}">Duplicate</LinkButton>
                            {/if}
                        </SeriesPermissionCheck>
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