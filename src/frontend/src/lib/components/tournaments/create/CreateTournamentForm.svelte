<script lang="ts">
    import { onMount } from "svelte";
    import type { TournamentTemplate } from "$lib/types/tournaments/create/tournament-template";
    import Section from "$lib/components/common/Section.svelte";
    import SeriesSearch from "$lib/components/common/SeriesSearch.svelte";
    import type { TournamentSeries } from "$lib/types/tournaments/series/tournament-series";
    import { valid_games, valid_modes, mode_names } from "$lib/util/util";

    export let template_id: number | null = null;
    let template: TournamentTemplate | null = null;

    let date_option = "true";

    let series: TournamentSeries | null = null;

    let game = 'mk8dx';
    let mode = '150cc';
    let is_squad = "false";
    let teams_allowed = "false";
    let teams_only = "false";
    let team_members_only = "false";
    let checkins_open = "false";
    let min_players_checkin: number | null = null;

    onMount(async() => {
        if(!template_id) {
            return;
        }
        const res = await fetch(`/api/tournaments/templates/${template_id}`);
        if(res.status === 200) {
            const body: TournamentTemplate = await res.json();
            template = body;
            game = template.game;
            mode = template.mode;
            is_squad = String(template.is_squad);
            teams_allowed = String(template.teams_allowed);
            teams_only = String(template.teams_only);
            team_members_only = String(template.team_members_only);
            checkins_open = String(template.checkins_open);
            min_players_checkin = template.min_players_checkin;
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
                    <input name="date_start" type="datetime-local" required/>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="date_end">End Date</label>
                </div>
                <div>
                    <input name="date_end" type="datetime-local"/>
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
    <Section header="Tournament Format">
        <div class="option">
            <div>
                <label for="organizer">Organized by</label>
            </div>
            <div>
                <select name="organizer">
                    <option value="MKCentral">MKCentral</option>
                    <option value="Affiliate">Affiliate</option>
                    <option value="LAN">LAN</option>
                </select>
            </div>
        </div>
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
                    <option value="false">Solo</option>
                    <option value="true">Squad/Team</option>
                </select>
            </div>
        </div>
        {#if is_squad === "true"}
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
                        <select name="squad_tag_required">
                            <option value="false">No</option>
                            <option value="true">Yes</option>
                        </select>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="squad_name_required">Squad Name required for registration (this cannot be changed)</label>
                    </div>
                    <div>
                        <select name="squad_name_required">
                            <option value="false">No</option>
                            <option value="true">Yes</option>
                        </select>
                    </div>
                </div>
                <div class="option">
                    <div>
                        <label for="teams_allowed">Teams allowed?</label>
                    </div>
                    <div>
                        <select name="teams_allowed" bind:value={teams_allowed}>
                            <option value="false">No</option>
                            <option value="true">Yes</option>
                        </select>
                    </div>
                </div>
                {#if teams_allowed === "true"}
                    <div class="indented">
                        <div class="option">
                            <div>
                                <label for="teams_only">Teams only?</label>
                            </div>
                            <div>
                                <select name="teams_only" bind:value={teams_only}>
                                    <option value="false">No</option>
                                    <option value="true">Yes</option>
                                </select>
                            </div>
                        </div>
                        {#if teams_only === "true"}
                            <div class="indented option">
                                <div>
                                    <label for="team_members_only">Team members only?</label>
                                </div>
                                <div>
                                    <select name="team_members_only" bind:value={team_members_only}>
                                        <option value="false">No</option>
                                        <option value="true">Yes</option>
                                    </select>
                                </div>
                            </div>
                        {/if}
                    </div>
                {/if}
            </div>
        {/if}
        {#if teams_allowed === "false"}
            <div class="option">
                <div>
                    <label for="host_status_required">Can/can't host required?</label>
                </div>
                <div>
                    <select name="host_status_required">
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                    </select>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="mii_name_required">In-Game/Mii Name required?</label>
                </div>
                <div>
                    <select name="mii_name_required">
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                    </select>
                </div>
            </div>
            <div class="option">
                <div>
                    <label for="checkins_open">Check-ins enabled</label>
                </div>
                <div>
                    <select name="checkins_open" bind:value={checkins_open}>
                        <option value="false">No</option>
                        <option value="true">Yes</option>
                    </select>
                </div>
            </div>
            {#if checkins_open === "true" && is_squad === "true"}
                <div class="option indented">
                    <div>
                        <label for="min_players_checkin">Minimum Check-ins per Squad</label>
                    </div>
                    <div>
                        <input class="number" type="number" name="min_players_checkin" bind:value={min_players_checkin} min=1 max=99/>
                    </div>
                </div>
            {/if}
        {/if}
        <div class="option">
            <div>
                <label for="verification_required">Verification required</label>
            </div>
            <div>
                <select name="verification_required">
                    <option value="false">No</option>
                    <option value="true">Yes</option>
                </select>
            </div>
        </div>
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
</style>