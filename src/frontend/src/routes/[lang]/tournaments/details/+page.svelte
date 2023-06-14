<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import type { Tournament } from '$lib/types/Tournament';

    let id = 0;
    let tournament_found = true;

    let t: Tournament;

    onMount(async () => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);
        const res = await fetch(`/api/tournaments/${id}`);
        if(res.status !== 200) {
            tournament_found = false;
            return;
        }
        const body: Tournament = await res.json();
        //console.log(body.tournament_name);
        t = body;
    });
</script>

<h1>{id}</h1>
{#if t}
{t.tournament_name}
{/if}