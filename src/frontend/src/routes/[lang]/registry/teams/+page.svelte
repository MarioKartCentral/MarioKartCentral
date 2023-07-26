<script lang="ts">
    import { onMount } from 'svelte';
    import type { Team } from '$lib/types/team';
    import TeamListItem from '$lib/components/TeamListItem.svelte';

    let teams: Team[] = [];

    onMount(async () => {
        const res = await fetch('/api/registry/teams');
        if(res.status === 200) {
            const body = await res.json();
            for(let t of body) {
                teams.push(t);
            }
            teams=teams;
        }
    });
</script>

<div class="container">
    <h2>Teams</h2>
    <table>
        <col class="tag">
        <col class="name">
        <thead>
            <tr>
                <th>Tag</th>
                <th>Name</th>
            </tr>
        </thead>
        <tbody>
            {#each teams as team}
                <TeamListItem team={team}/>
            {/each}
        </tbody>
    </table>
    
</div>

<style>
    div.container {
        width: 50%;
        margin: 20px auto 20px auto;
    }
    table {
        background-color: black;
        border-collapse: collapse;
        width: 100%;
    }
    thead {
        background-color: green;
    }
    td {
        padding: 10px;
        text-align: center;
    }
    col.tag {
        width: 20%;
    }
    col.name {
        width: 80%;
    }
    
</style>