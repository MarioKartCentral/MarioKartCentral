<script lang="ts">
    import { onMount } from "svelte";
    import type { TournamentTemplateMinimal } from "$lib/types/tournaments/create/tournament-template-minimal";
    import Section from "$lib/components/common/Section.svelte";
    import Table from "$lib/components/common/Table.svelte";
    import { page } from "$app/stores";

    export let series_id: number | null = null;

    let templates: TournamentTemplateMinimal[] = [];

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

<Section header="Select Template">
    <Table>
        {#each templates as template, i}
            <tr class="row-{i%2}">
                <a href="/{$page.params.lang}/tournaments/create?template_id={template.id}">{template.template_name}</a>
            </tr>
        {/each}
    </Table>    
</Section>
