<script lang="ts">
    import { onMount } from "svelte";
    import type { TournamentTemplate } from "$lib/types/tournaments/create/tournament-template";
    import Section from "$lib/components/common/Section.svelte";
    import SeriesSearch from "$lib/components/common/SeriesSearch.svelte";
    import type { TournamentSeries } from "$lib/types/tournaments/series/tournament-series";

    export let template_id: number | null = null;
    let template: TournamentTemplate | null = null;

    let date_option = "true";

    let series: TournamentSeries | null = null;

    onMount(async() => {
        if(!template_id) {
            return;
        }
        const res = await fetch(`/api/tournaments/templates/${template_id}`);
        if(res.status === 200) {
            const body: TournamentTemplate = await res.json();
            template = body;
        }
    });
</script>

<form method="POST">
    <Section header="New Tournament">
        <div class="option">
            <div>
                <label for="tournament_name">Tournament Name (required)</label>
            </div>
            <div>
                <input name="tournament_name" class="tournament_name" type="text" required value={template ? template.tournament_name : ""}/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="tournament_series">Tournament Series</label>
            </div>
            <div>
                <SeriesSearch bind:option={series}/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="date_type">Date</label>
            </div>
            <div>
                <select name="date_type" bind:value={date_option} required>
                    <option value="true">Specify</option>
                    <option value="false">TBD</option>
                </select>
            </div>
        </div>
        {#if date_option === "true"}
            <div class="option">
                <div>
                    <label for="date_start">Start Date</label>
                </div>
                <div>
                    <input name="date_start" type="date" required/>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="date_end">End Date</label>
                </div>
                <div>
                    <input name="date_end" type="date"/>
                </div>
            </div>
        {/if}
        <div class="option">
            <div>
                <label for="logo">Logo</label>
            </div>
            <div>
                <input name="logo" type="text"/>
            </div>
        </div>
    </Section>
</form>

<style>
    div.option {
        margin-bottom: 10px;
    }
    input.tournament_name {
        width: 90%;
    }
</style>