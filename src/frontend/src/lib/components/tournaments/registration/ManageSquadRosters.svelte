<script lang="ts">
    import Dialog from "$lib/components/common/Dialog.svelte";
    import type { RosterBasic } from "$lib/types/roster-basic";
    import type { Tournament } from "$lib/types/tournament";
    import type { TournamentSquad } from "$lib/types/tournament-squad";
    import TagBadge from "$lib/components/badges/TagBadge.svelte";
    import CancelButton from "$lib/components/common/buttons/CancelButton.svelte";
    import type { TeamRoster } from "$lib/types/team-roster";
    import { onMount } from "svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import RosterSearch from "$lib/components/common/RosterSearch.svelte";
    import LL from "$i18n/i18n-svelte";

    export let tournament: Tournament;
    export let is_privileged = false;

    let squad: TournamentSquad;
    let manage_rosters_dialog: Dialog;
    let registerable_rosters: TeamRoster[] = [];
    let selected_roster: TeamRoster | null = null;

    export function open(s: TournamentSquad) {
        squad = s;
        manage_rosters_dialog.open();
    }

    onMount(async () => {
        if(is_privileged) return; 
        const res = await fetch(
            `/api/registry/teams/getRegisterable?tournament_id=${tournament.id}&game=${tournament.game}&mode=${tournament.mode}`,
        );
        if (res.status < 300) {
            const body: TeamRoster[] = await res.json();
            registerable_rosters = body;
        }
    });
    
    async function addRoster(roster: TeamRoster | null) {
        if(roster === null) {
            return;
        }
        let conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.ADD_ROSTER_CONFIRM({roster_name: roster.name}));
        if(!conf) return;
        const payload = {
            registration_id: squad.id,
            roster_id: roster.id
        }
        const endpoint = is_privileged ? `/api/tournaments/${tournament.id}/forceAddRosterToSquad` : `/api/tournaments/${tournament.id}/addRosterToSquad`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.TOURNAMENTS.REGISTRATIONS.ADD_ROSTER_FAILED()}: ${result['title']}`);
        }
    }

    async function removeRoster(roster: RosterBasic) {
        let conf = window.confirm($LL.TOURNAMENTS.REGISTRATIONS.REMOVE_ROSTER_CONFIRM({roster_name: String(roster.roster_name)}));
        if(!conf) return;
            const payload = {
            registration_id: squad.id,
            roster_id: roster.roster_id
        }
        const endpoint = is_privileged ? `/api/tournaments/${tournament.id}/forceRemoveRosterFromSquad` : `/api/tournaments/${tournament.id}/removeRosterFromSquad`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`${$LL.TOURNAMENTS.REGISTRATIONS.REMOVE_ROSTER_FAILED()}: ${result['title']}`);
        }
    }
</script>

<Dialog bind:this={manage_rosters_dialog} header={$LL.TOURNAMENTS.REGISTRATIONS.MANAGE_ROSTERS()}>
    {#if squad}
        <div class="registered-rosters">
            {#each squad.rosters as roster}
                <div class="team-roster">
                    <div>
                        <TagBadge tag={roster.roster_tag}/>
                    </div>
                    <div>
                        {roster.roster_name}
                    </div>
                    {#if squad.rosters.length > 1}
                        <div>
                            <CancelButton on:click={() => removeRoster(roster)}/>
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
        <div class="add-roster">
            {#if is_privileged}
                <div>{$LL.TOURNAMENTS.REGISTRATIONS.ADD_ROSTER()}</div>
                <div>
                    <RosterSearch bind:roster={selected_roster} game={tournament.game} mode={tournament.mode} is_active={null} is_historical={null}/>
                </div>
            {:else if registerable_rosters.length}
            <div>{$LL.TOURNAMENTS.REGISTRATIONS.ADD_ROSTER()}</div>
                <div>
                    <select bind:value={selected_roster}>
                        <option value={null}>{$LL.TOURNAMENTS.REGISTRATIONS.SELECT_A_ROSTER()}</option>
                        {#each registerable_rosters as roster}
                            <option value={roster}>{roster.name}</option>
                        {/each}
                    </select>
                </div>
            {/if}
            {#if selected_roster !== null}
                <div class="button">
                    <Button on:click={() => addRoster(selected_roster)}>{$LL.TOURNAMENTS.REGISTRATIONS.ADD_ROSTER()}</Button>
                </div>
            {/if}
        </div>
        
    {/if}
    
</Dialog>

<style>
    div.registered-rosters {
        margin-bottom: 5px;
    }
    div.team-roster {
        display: flex;
        gap: 5px;
        margin-bottom: 5px;
        align-items: center;
    }
    div.add-roster {
        margin-top: 10px;
    }
    div.button {
        margin-top: 5px;
    }
</style>