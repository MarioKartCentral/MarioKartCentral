<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import type { Team } from "$lib/types/team";
    import TeamSearch from "$lib/components/common/TeamSearch.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

    let from_team: Team | null = null;
    let to_team: Team | null = null;

    async function mergeTeams() {
        if(!from_team || !to_team) {
            return;
        }
        if(from_team.id == to_team.id) {
            alert("Please select two different teams");
            return;
        }
        let conf = window.confirm(`Are you sure you want to merge all of ${from_team.name}'s data into ${to_team.name}? This will DELETE ${from_team.name} completely.`);
        if(!conf) return;
        const payload = {
            from_team_id: from_team.id,
            to_team_id: to_team.id,
        };
        const endpoint = "/api/registry/teams/merge";
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (res.status < 300) {
            alert('Successfully merged teams!');
            window.location.reload();
        } else {
            alert(`Merging teams failed: ${result['title']}`);
        }
    }
</script>

<Section header="Merge Teams">
    <div class="option">
        <div>
            Old Team:
        </div>
        <TeamSearch bind:team={from_team}/>
    </div>
    
    {#if from_team}
        <div class="option">
            <div>New Team:</div>
            <TeamSearch bind:team={to_team}/>
        </div>
        
    {/if}
    {#if to_team}
        <Button on:click={mergeTeams}>Merge Teams</Button>
    {/if}
</Section>

<style>
    div.option {
        margin-bottom: 10px;
    }
</style>