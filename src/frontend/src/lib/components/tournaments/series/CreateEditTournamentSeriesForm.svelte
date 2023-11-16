<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { CreateTournamentSeries } from "$lib/types/tournaments/series/create/create-tournament-series";
    import GameModeSelect from "$lib/components/common/GameModeSelect.svelte";
    import MarkdownBox from "$lib/components/common/MarkdownBox.svelte";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import { onMount } from "svelte";

    export let series_id: number | null = null;
    export let is_edit: boolean = false;

    let data: CreateTournamentSeries = {
        series_name: "",
        url: null,
        organizer: "MKCentral",
        location: null,
        display_order: 0,
        game: "mk8dx",
        mode: "150cc",
        is_historical: false,
        is_public: true,
        description: "",
        ruleset: "",
        logo: null
    };

    onMount(async() => {
        if(!series_id) {
            return;
        }
        const res = await fetch(`/api/tournaments/series/${series_id}`);
        if(res.status === 200) {
            const body: CreateTournamentSeries = await res.json();
            data = Object.assign(data, body);
        }
    });

    function updateData() {
        data = data;
    }
    async function createSeries(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        let payload = data;
        console.log(payload);
        const endpoint = '/api/tournaments/series/create';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            goto(`/${$page.params.lang}/tournaments/series`);
            alert('Successfully created series!');
        } else {
            alert(`Creating series failed: ${result['title']}`);
        }
    }
    async function editSeries(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        let payload = data;
        console.log(payload);
        const endpoint = `/api/tournaments/series/${series_id}/edit`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            goto(`/${$page.params.lang}/tournaments/series/details?id=${series_id}`);
            alert('Successfully edited series!');
        } else {
            alert(`Editing series failed: ${result['title']}`);
        }
    }
</script>

<form method="POST" on:submit|preventDefault={is_edit ? editSeries : createSeries}>
    <Section header={is_edit ? "Edit Tournament Series" : "Create Tournament Series"}>
        <div class="option">
            <div>
                <label for="series_name">Series Name</label>
            </div>
            <div>
                <input type="text" name="series_name" bind:value={data.series_name} minlength=1 required/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="url">Series URL</label>
            </div>
            <div>
                <input type="text" name="url" bind:value={data.url}/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="display_order">Display Order</label>
            </div>
            <div>
                <input type="number" name="display_order" bind:value={data.display_order} min=0 required/>
            </div>
        </div>
        <div class="logo">
            <div>
                <label for="logo">Logo</label>
            </div>
            <div>
                <input type="text" name="logo" bind:value={data.logo}/>
            </div>
        </div>
    </Section>
    <Section header="Event Defaults">
        <div class="option">
            <div>
                <label for="organizer">Organized by</label>
            </div>
            <div>
                <select name="organizer" bind:value={data.organizer} on:change={updateData}>
                    <option value="MKCentral">MKCentral</option>
                    <option value="Affiliate">Affiliate</option>
                    <option value="LAN">LAN</option>
                </select>
            </div>
        </div>
        {#if data.organizer === 'LAN'}
            <div class="option">
                <div>
                    <label for="location">Location</label>
                </div>
                <div>
                    <input name="location" type="text" bind:value={data.location}/>
                </div>
            </div>
        {/if}
        <GameModeSelect bind:game={data.game} bind:mode={data.mode}/>
    </Section>
    <Section header="Description/Ruleset">
        <div class="option">
            <div>
                <label for="description">Series Description</label>
            </div>
            <div>
                <textarea name="description" bind:value={data.description} on:change={updateData}/>
            </div>
            <div>Description Preview</div>
            <div>
                <MarkdownBox content={data.description}/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="ruleset">Series Ruleset</label>
            </div>
            <div>
                <textarea name="ruleset" bind:value={data.ruleset} on:change={updateData}/>
            </div>
            <div>Description Preview</div>
            <div>
                <MarkdownBox content={data.ruleset}/>
            </div>
        </div>
    </Section>
    <Section header="Visibility">
        <div class="option">
            <div>
                <label for="is_public">Show on Tournament Series listing</label>
            </div>
            <div>
                <select name="is_public" bind:value={data.is_public}>
                    <option value={true}>Show</option>
                    <option value={false}>Hide</option>
                </select>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="is_historical">Active/Historical</label>
            </div>
            <div>
                <select name="is_historical" bind:value={data.is_historical}>
                    <option value={false}>Active</option>
                    <option value={true}>Historical</option>
                </select>
            </div>
        </div>
    </Section>
    <Section header="Submit">
        <button type="submit">{is_edit ? "Edit Series" : "Create Series"}</button>
    </Section>
</form>

<style>
    div.option {
        margin-bottom: 10px;
    }
</style>