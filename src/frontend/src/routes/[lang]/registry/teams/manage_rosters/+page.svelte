<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import Dialog from "$lib/components/common/Dialog.svelte";
    import type { Team } from '$lib/types/team';
    import { setTeamPerms, team_permissions } from '$lib/util/util';
    import TeamRosterManage from '$lib/components/registry/teams/TeamRosterManage.svelte';

    let dialog: Dialog;
    let id = 0;
    let team: Team;
    $: team_name = team ? team.name : 'Registry';

    setTeamPerms();

    onMount(async () => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);
        const res = await fetch(`/api/registry/teams/${id}`);
        if (res.status != 200) {
            return;
        }
        const body: Team = await res.json();
        team = body;
    });
</script>

<svelte:head>
  <title>{team_name} | Mario Kart Central</title>
</svelte:head>

<button on:click={() => dialog.open()}>Hey!</button>

<Dialog bind:this={dialog} header="Test Dialog">
    hi!!!!!!!!!!!!!!!!
</Dialog>

{#if team}
    {#each team.rosters as roster}
        <TeamRosterManage roster={roster}/>
    {/each}
{/if}