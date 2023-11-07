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

    export let template_id: number | null = null;
    let template: TournamentTemplate | null = null;

    let series: TournamentSeries | null = null;

    // binded fields in the form to customize which options appear
    let organizer = 'MKCentral';
    let game = 'mk8dx';
    let mode = '150cc';
    let is_squad = false;
    let teams_allowed = false;
    let teams_only = false;
    let checkins_open = false;
    let min_players_checkin: number | null = null;
    let description = "";
    let use_series_description = false;
    let ruleset = "";
    let use_series_ruleset = false;
    let is_viewable = true;

    onMount(async() => {
        if(!template_id) {
            return;
        }
        const res = await fetch(`/api/tournaments/templates/${template_id}`);
        if(res.status === 200) {
            const body: TournamentTemplate = await res.json();
            template = body;
            organizer = template.organizer;
            game = template.game;
            mode = template.mode;
            is_squad = template.is_squad;
            teams_allowed = template.teams_allowed;
            teams_only = template.teams_only;
            checkins_open = template.checkins_open;
            min_players_checkin = template.min_players_checkin;
            description = template.description;
            use_series_description = template.use_series_description;
            ruleset = template.ruleset;
            use_series_ruleset = template.use_series_ruleset;
            is_viewable = template.is_viewable;
        }
    });

    async function createTournament(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        function getValue(name: string) {
            return data.get(name) ? data.get(name)?.toString() : null;
        }
        function getNumValue(name: string) {
            return data.get(name) ? Number(data.get(name)) : null;
        }
        function getDate(name: string) {
            let date_form = data.get(name);
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
        
        const payload = {
            tournament_name: getValue("tournament_name"),
            series_id: series ? series.id : null,
            date_start: date_start,
            date_end: date_end,
            logo: getValue('logo'),
            url: null,
            organizer: getValue('organizer'),
            location: getValue('location'),
            game: getValue('game'),
            mode: getValue('mode'),
            // quick hack to convert back to boolean
            is_squad: getValue('is_squad') === 'true',
            min_squad_size: getNumValue('min_squad_size'),
            max_squad_size: getNumValue('max_squad_size'),
            
            squad_tag_required: getValue('squad_tag_required') === 'true',
            squad_name_required: getValue('squad_name_required') === 'true',
            teams_allowed: getValue('teams_allowed') === 'true',
            teams_only: getValue('teams_only') === 'true',
            team_members_only: getValue('team_members_only') === 'true',
            min_representatives: getValue('min_representatives'),
            host_status_required: getValue('host_status_required') === 'true',
            mii_name_required: getValue('mii_name_required') === 'true',
            require_single_fc: getValue('require_single_fc') === 'true',
            checkins_open: getValue('checkins_open') === 'true',
            min_players_checkin: getNumValue('min_players_checkin'),
            verification_required: getValue('verification_required') === 'true',
            use_series_description: getValue('use_series_description') === 'true',
            description: getValue('description'),
            use_series_ruleset: getValue('use_series_ruleset') === 'true',
            ruleset: getValue('ruleset'),
            registrations_open: getValue('registrations_open') === 'true',
            registration_deadline: registration_deadline,
            registration_cap: getNumValue('registration-cap'),
            is_viewable: getValue('is_viewable') === 'true',
            is_public: getValue('is_public') === 'true',
            show_on_profiles: getValue('show_on_profiles') === 'true',
            series_stats_include: getValue('series_stats_include') === 'true',
            verified_fc_required: false,
        };
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
            alert('Successfully created tournament..');
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
                <input name="tournament_name" class="tournament_name" type="text" required value={template ? template.tournament_name : ""}/>
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
                <select name="organizer" bind:value={organizer}>
                    <option value="MKCentral">MKCentral</option>
                    <option value="Affiliate">Affiliate</option>
                    <option value="LAN">LAN</option>
                </select>
            </div>
        </div>
        {#if organizer === 'LAN'}
            <div class="option">
                <div>
                    <label for="location">Location</label>
                </div>
                <div>
                    <input name="location" type="text" value={template ? template.location : ""}/>
                </div>
            </div>
        {/if}
        <div class="option">
            <div>
                <label for="game">Game</label>
            </div>
            <div>
                <select name="game" bind:value={game} on:change={() => ([mode] = valid_modes[game])}>
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
                <select name="mode" bind:value={mode}>
                    {#each valid_modes[game] as mode}
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
                <select name="is_squad" bind:value={is_squad}>
                    <option value={false}>Solo</option>
                    <option value={true}>Squad/Team</option>
                </select>
            </div>
        </div>
        {#if is_squad}
            <div class="indented">
                <div class="option">
                    <div>
                        <label for="min_squad_size">Minimum Players per Squad</label>
                    </div>
                    <div>
                        <input class="number" type="number" name="min_squad_size" min=1 max=99/>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="max_squad_size">Maximum Players per Squad</label>
                    </div>
                    <div>
                        <input class="number" type="number" name="max_squad_size" min=1 max=99/>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="squad_tag_required">Squad Tag required for registration (this cannot be changed)</label>
                    </div>
                    <div>
                        <select name="squad_tag_required" value={template ? template.squad_tag_required : false}>
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
                        <select name="squad_name_required" value={template ? template.squad_name_required : false}>
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
                        <select name="teams_allowed" bind:value={teams_allowed}>
                            <option value={false}>No</option>
                            <option value={true}>Yes</option>
                        </select>
                    </div>
                </div>
                {#if teams_allowed}
                    <div class="indented">
                        <div class="option">
                            <div>
                                <label for="teams_only">Teams only? (this cannot be changed)</label>
                            </div>
                            <div>
                                <select name="teams_only" bind:value={teams_only}>
                                    <option value={false}>No</option>
                                    <option value={true}>Yes</option>
                                </select>
                            </div>
                        </div>
                        {#if teams_only}
                            <div class="indented option">
                                <div>
                                    <label for="team_members_only">Team members only? (this cannot be changed)</label>
                                </div>
                                <div>
                                    <select name="team_members_only" value={template ? template.team_members_only : false}>
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
                                    <input class="number" type="number" name="min_representatives" value={template ? template.min_representatives : 0} min=0 max=3 required/>
                                </div>
                            </div>
                        {/if}
                    </div>
                {/if}
            </div>
        {/if}
        {#if !is_squad || !teams_allowed}
            <div class="option">
                <div>
                    <label for="host_status_required">Can/can't host required? (this cannot be changed)</label>
                </div>
                <div>
                    <select name="host_status_required" value={template ? template.host_status_required : false}>
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
                    <select name="mii_name_required" value={template ? template.mii_name_required : false}>
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
                    <select name="require_single_fc" value={template ? template.require_single_fc : false}>
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
                    <select name="checkins_open" bind:value={checkins_open}>
                        <option value={false}>No</option>
                        <option value={true}>Yes</option>
                    </select>
                </div>
            </div>
            {#if checkins_open && is_squad}
                <div class="option indented">
                    <div>
                        <label for="min_players_checkin">Minimum Check-ins per Squad</label>
                    </div>
                    <div>
                        <input class="number" type="number" name="min_players_checkin" bind:value={min_players_checkin} min=1 max=99 required/>
                    </div>
                </div>
            {/if}
        {/if}
        <div class="option">
            <div>
                <label for="verification_required">Verification required</label>
            </div>
            <div>
                <select name="verification_required" value={template ? template.verification_required : false}>
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
                    <select name="use_series_description" bind:value={use_series_description}>
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
                {#if series && use_series_description}
                    <textarea name="description" value={series.description} disabled/>
                {:else}
                    <textarea name="description" bind:value={description}/>
                {/if}
            </div>
            <div>Description Preview</div>
            <div class="preview">
                <MarkdownBox content={series && use_series_description ? series.description : description}/>
            </div>
        </div>
        {#if series}
            <div class="option">
                <div>
                    <label for="use_series_ruleset">Use series ruleset?</label>
                </div>
                <div>
                    <select name="use_series_ruleset" bind:value={use_series_ruleset}>
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
                {#if series && use_series_ruleset}
                    <textarea name="ruleset" value={series.ruleset} disabled/>
                {:else}
                    <textarea name="ruleset" bind:value={ruleset}/>
                {/if}
            </div>
            <div>Ruleset Preview</div>
            <div class="preview">
                <MarkdownBox content={series && use_series_ruleset ? series.ruleset : ruleset}/>
            </div>
        </div>
    </Section>
    <Section header="Tournament Registration">
        <div class="option">
            <div>
                <label for="registrations_open">Registrations open?</label>
            </div>
            <div>
                <select name="registrations_open" value={template ? template.registrations_open : true}>
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
                <input name="registration_cap" type="number" min=0/>
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
                <select name="is_viewable" bind:value={is_viewable}>
                    <option value={true}>Yes</option>
                    <option value={false}>No</option>
                </select>
            </div>
        </div>
        {#if is_viewable}
            <div class="option indented">
                <div>
                    <label for="is_public">
                        Show on tournament listing?
                    </label>
                </div>
                <div>
                    <select name="is_public" value={template ? template.is_public : true}>
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
                <select name="show_on_profiles" value={template ? template.show_on_profiles : true}>
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
                    <select name="series_stats_include" value={template ? template.series_stats_include : true}>
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