<script lang="ts">
    import { onMount } from "svelte";
    import type { TournamentTemplate } from "$lib/types/tournaments/create/tournament-template";
    import Section from "$lib/components/common/Section.svelte";
    import SeriesSearch from "$lib/components/common/SeriesSearch.svelte";
    import type { TournamentSeries } from "$lib/types/tournaments/series/tournament-series";
    import { valid_games, valid_modes, mode_names } from "$lib/util/util";
    import MarkdownBox from "$lib/components/common/MarkdownBox.svelte";
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import type { CreateTournament } from "$lib/types/tournaments/create/create-tournament";

    export let template_id: number | null = null;
    let template: TournamentTemplate | null = null;

    let series: TournamentSeries | null = null;

    let data: CreateTournament = {
        tournament_name: "",
        series_id: null,
        date_start: null,
        date_end: null,
        logo: null,
        url: null,
        organizer: "MKCentral",
        location: null,
        game: "mk8dx",
        mode: "150cc",
        is_squad: false,
        min_squad_size: null,
        max_squad_size: null,
        squad_tag_required: false,
        squad_name_required: false,
        teams_allowed: false,
        teams_only: false,
        team_members_only: false,
        min_representatives: null,
        host_status_required: false,
        mii_name_required: false,
        require_single_fc: false,
        checkins_open: false,
        min_players_checkin: null,
        verification_required: false,
        use_series_description: false,
        description: "",
        use_series_ruleset: false,
        ruleset: "",
        registrations_open: false,
        registration_cap: null,
        registration_deadline: null,
        is_viewable: true,
        is_public: true,
        show_on_profiles: true,
        series_stats_include: false,
        verified_fc_required: false,
    };

    function updateData() {
        if(data.organizer != "LAN") {
            data.location = null;
        }
        if(data.teams_allowed) {
            data.mii_name_required = false;
            data.host_status_required = false;
            data.require_single_fc = false;
            if(!data.teams_only) {
                data.team_members_only = false;
                data.min_representatives = null;
            }
        }
        else {
            data.teams_only = false;
            data.team_members_only = false;
        }
        if(!data.is_squad) {
            data.min_squad_size = null;
            data.max_squad_size = null;
            data.squad_tag_required = false;
            data.squad_name_required = false;
            data.teams_allowed = false;
            data.teams_only = false;
            data.team_members_only = false;
            data.min_representatives = null;
        }
        if(!data.checkins_open) {
            data.min_players_checkin = null;
        }
        data = data;
    }

    onMount(async() => {
        if(!template_id) {
            return;
        }
        const res = await fetch(`/api/tournaments/templates/${template_id}`);
        if(res.status === 200) {
            const body: TournamentTemplate = await res.json();
            template = body;
            data = Object.assign(data, template);
        }
    });

    async function createTournament(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        function getDate(name: string) {
            let date_form = formData.get(name);
            if(!date_form) {
                return null;
            }
            let date = new Date(date_form.toString());
            return date.getTime() / 1000; //return date in seconds
        }

        let date_start: number | null = getDate("date_start");
        let date_end: number | null = getDate("date_end");
        let registration_deadline: number | null = getDate("registration_deadline");
        if(date_start && date_end && date_start > date_end) {
            alert("Starting date must be after ending date");
            return;
        }
        data.series_id = series ? series.id : null;
        data.date_start = date_start;
        data.date_end = date_end;
        data.registration_deadline = registration_deadline;
        
        if(!data.series_id) {
            data.use_series_description = false;
            data.use_series_ruleset = false;
            data.series_stats_include = false;
        }
        
        let payload = data;
        console.log(payload);
        const endpoint = '/api/tournaments/create';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            goto(`/${$page.params.lang}/tournaments`);
            alert('Successfully created tournament!');
        } else {
            alert(`Creating tournament failed: ${result['title']}`);
        }
    }
</script>

<form method="POST" on:submit|preventDefault={createTournament}>
    <Section header="New Tournament">
        <div class="option">
            <div>
                <label for="tournament_name">Tournament Name (required)</label>
            </div>
            <div>
                <input name="tournament_name" class="tournament_name" type="text" bind:value={data.tournament_name} minlength=1 required/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="tournament_series">Tournament Series</label>
            </div>
            <div>
                {#if template}
                    <SeriesSearch bind:option={series} series_id={template.series_id}/>
                {:else}
                    <SeriesSearch bind:option={series}/>
                {/if}
            </div>
        </div>
        <div class="option">
            <div>
                <label for="date_start">Start Date</label>
            </div>
            <div>
                <input name="date_start" type="datetime-local" required/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="date_end">End Date</label>
            </div>
            <div>
                <input name="date_end" type="datetime-local" required/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="logo">Logo</label>
            </div>
            <div>
                <input name="logo" type="text"/>
            </div>
        </div>
    </Section>
    <Section header="Tournament Format">
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
        <div class="option">
            <div>
                <label for="game">Game</label>
            </div>
            <div>
                <select name="game" bind:value={data.game} on:change={() => {
                    [data.mode] = valid_modes[data.game];
                    updateData();
                }}>
                    {#each Object.keys(valid_games) as game}
                        <option value={game}>{valid_games[game]}</option>
                    {/each}
                </select>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="mode">Mode</label>
            </div>
            <div>
                <select name="mode" bind:value={data.mode}>
                    {#each valid_modes[data.game] as mode}
                        <option value={mode}>{mode_names[mode]}</option>
                    {/each}
                </select>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="is_squad">Registration format (this cannot be changed)</label>
            </div>
            <div>
                <select name="is_squad" bind:value={data.is_squad} on:change={updateData}>
                    <option value={false}>Solo</option>
                    <option value={true}>Squad/Team</option>
                </select>
            </div>
        </div>
        {#if data.is_squad}
            <div class="indented">
                <div class="option">
                    <div>
                        <label for="min_squad_size">Minimum Players per Squad</label>
                    </div>
                    <div>
                        <input class="number" type="number" name="min_squad_size" min=1 max=99 bind:value={data.min_squad_size}/>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="max_squad_size">Maximum Players per Squad</label>
                    </div>
                    <div>
                        <input class="number" type="number" name="max_squad_size" min=1 max=99 bind:value={data.max_squad_size}/>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="squad_tag_required">Squad Tag required for registration (this cannot be changed)</label>
                    </div>
                    <div>
                        <select name="squad_tag_required" bind:value={data.squad_tag_required}>
                            <option value={false}>No</option>
                            <option value={true}>Yes</option>
                        </select>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="squad_name_required">Squad Name required for registration (this cannot be changed)</label>
                    </div>
                    <div>
                        <select name="squad_name_required" bind:value={data.squad_name_required}>
                            <option value={false}>No</option>
                            <option value={true}>Yes</option>
                        </select>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="teams_allowed">Teams allowed? (this cannot be changed)</label>
                    </div>
                    <div>
                        <select name="teams_allowed" bind:value={data.teams_allowed} on:change={updateData}>
                            <option value={false}>No</option>
                            <option value={true}>Yes</option>
                        </select>
                    </div>
                </div>
                {#if data.teams_allowed}
                    <div class="indented">
                        <div class="option">
                            <div>
                                <label for="teams_only">Teams only? (this cannot be changed)</label>
                            </div>
                            <div>
                                <select name="teams_only" bind:value={data.teams_only} on:change={updateData}>
                                    <option value={false}>No</option>
                                    <option value={true}>Yes</option>
                                </select>
                            </div>
                        </div>
                        {#if data.teams_only}
                            <div class="indented option">
                                <div>
                                    <label for="team_members_only">Team members only? (this cannot be changed)</label>
                                </div>
                                <div>
                                    <select name="team_members_only" bind:value={data.team_members_only}>
                                        <option value={false}>No</option>
                                        <option value={true}>Yes</option>
                                    </select>
                                </div>
                            </div>
                            <div class="indented option">
                                <div>
                                    <label for="min_representatives"># of representatives required</label>
                                </div>
                                <div>
                                    <input class="number" type="number" name="min_representatives" bind:value={data.min_representatives} min=0 max=3 required/>
                                </div>
                            </div>
                        {/if}
                    </div>
                {/if}
            </div>
        {/if}
        {#if !data.is_squad || !data.teams_allowed}
            <div class="option">
                <div>
                    <label for="host_status_required">Can/can't host required? (this cannot be changed)</label>
                </div>
                <div>
                    <select name="host_status_required" bind:value={data.host_status_required}>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="mii_name_required">In-Game/Mii Name required? (this cannot be changed)</label>
                </div>
                <div>
                    <select name="mii_name_required" bind:value={data.mii_name_required}>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="require_single_fc">Require participants to select one FC for the tournament? (this cannot be changed)</label>
                </div>
                <div>
                    <select name="require_single_fc" bind:value={data.require_single_fc}>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="checkins_open">Check-ins enabled</label>
                </div>
                <div>
                    <select name="checkins_open" bind:value={data.checkins_open} on:change={updateData}>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
            {#if data.checkins_open && data.is_squad}
                <div class="option indented">
                    <div>
                        <label for="min_players_checkin">Minimum Check-ins per Squad</label>
                    </div>
                    <div>
                        <input class="number" type="number" name="min_players_checkin" bind:value={data.min_players_checkin} min=1 max=99 required/>
                    </div>
                </div>
            {/if}
        {/if}
        <div class="option">
            <div>
                <label for="verification_required">Verification required</label>
            </div>
            <div>
                <select name="verification_required" bind:value={data.verification_required}>
                    <option value={false}>No</option>
                    <option value={true}>Yes</option>
                </select>
            </div>
        </div>
    </Section>
    <Section header="Tournament Info">
        {#if series}
            <div class="option">
                <div>
                    <label for="use_series_description">Use series description?</label>
                </div>
                <div>
                    <select name="use_series_description" bind:value={data.use_series_description} on:change={updateData}>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
        {/if}
        <div class="option">
            <div>
                <label for="description">Tournament Description</label>
            </div>
            <div>
                {#if series && data.use_series_description}
                    <textarea name="description" value={series.description} disabled/>
                {:else}
                    <textarea name="description" bind:value={data.description} on:change={updateData} minlength=1/>
                {/if}
            </div>
            <div>Description Preview</div>
            <div class="preview">
                <MarkdownBox content={series && data.use_series_description ? series.description : data.description}/>
            </div>
        </div>
        {#if series}
            <div class="option">
                <div>
                    <label for="use_series_ruleset">Use series ruleset?</label>
                </div>
                <div>
                    <select name="use_series_ruleset" bind:value={data.use_series_ruleset} on:change={updateData}>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
        {/if}
        <div class="option">
            <div>
                <label for="ruleset">Tournament Ruleset</label>
            </div>
            <div>
                {#if series && data.use_series_ruleset}
                    <textarea name="ruleset" value={series.ruleset} disabled/>
                {:else}
                    <textarea name="ruleset" bind:value={data.ruleset} minlength=1/>
                {/if}
            </div>
            <div>Ruleset Preview</div>
            <div class="preview">
                <MarkdownBox content={series && data.use_series_ruleset ? series.ruleset : data.ruleset}/>
            </div>
        </div>
    </Section>
    <Section header="Tournament Registration">
        <div class="option">
            <div>
                <label for="registrations_open">Registrations open?</label>
            </div>
            <div>
                <select name="registrations_open" bind:value={data.registrations_open}>
                    <option value={true}>Open</option>
                    <option value={false}>Closed</option>
                </select>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="registration_deadline">Registration Deadline (optional)</label>
            </div>
            <div>
                <input name="registration_deadline" type="datetime-local"/>
            </div>
        </div>
        <div class="option">
            <div>
                <label for="registration_cap">Registration Cap (optional)</label>
            </div>
            <div>
                <input name="registration_cap" type="number" min=0 bind:value={data.registration_cap}/>
            </div>
        </div>
    </Section>
    <Section header="Tournament Status">
        <div class="option">
            <div>
                <label for="is_viewable">
                    Have tournament publicly accessible with link?
                </label>
            </div>
            <div>
                <select name="is_viewable" bind:value={data.is_viewable} on:change={updateData}>
                    <option value={true}>Yes</option>
                    <option value={false}>No</option>
                </select>
            </div>
        </div>
        {#if data.is_viewable}
            <div class="option indented">
                <div>
                    <label for="is_public">
                        Show on tournament listing?
                    </label>
                </div>
                <div>
                    <select name="is_public" bind:value={data.is_public}>
                        <option value={true}>Show</option>
                        <option value={false}>Hide</option>
                    </select>
                </div>
            </div>
        {/if}
        <div class="option">
            <div>
                <label for="show_on_profiles">Show results on player profiles?</label>
            </div>
            <div>
                <select name="show_on_profiles" bind:value={data.show_on_profiles}>
                    <option value={true}>Show</option>
                    <option value={false}>Hide</option>
                </select>
            </div>
        </div>
        {#if series}
            <div class="option">
                <div>
                    <label for="series_stats_include">Include tournament in series stats?</label>
                </div>
                <div>
                    <select name="series_stats_include" bind:value={data.series_stats_include}>
                        <option value={true}>Yes</option>
                        <option value={false}>No</option>
                    </select>
                </div>
            </div>
        {/if}
        
    </Section>
    <Section header="Submit">
        <button type="submit">Create Tournament</button>
    </Section>
</form>

<style>
    div.option {
        margin-bottom: 10px;
    }
    div.indented {
        padding-left: 1em;
    }
    input.tournament_name {
        width: 90%;
    }
    input.number {
        width: 5%;
    }
    textarea {
        width: 50%;
    }
    div.preview {
        border: 1px;
    }
</style>