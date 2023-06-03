<script lang="ts">
    import { onMount } from 'svelte';
    import TournamentPageItem from '$lib/components/TournamentPageItem.svelte';

    let tournaments: Tournament[] = [];
    
    class Tournament {
        id: number;
        name: string;
        game: string;
        mode: string;
        date_start: Date;
        date_end: Date;

        constructor(id: number, name: string, game: string, mode: string, d_start: number, d_end: number) {
            this.id = id;
            this.name = name;
            this.game = game;
            this.mode = mode;
            this.date_start = new Date(d_start * 1000);
            this.date_end = new Date(d_end * 1000);
        }
    }

    onMount(async () => {
        const res = await fetch('/api/tournaments/list');
        if(res.status === 200) {
            const body = await res.json();
            for(let t of body) {
                let tournament = new Tournament(t.id, t.tournament_name, t.game, t.mode, t.date_start, t.date_end);
                tournaments.push(tournament);
            }
            tournaments=tournaments;
        }
    });
</script>

<h1>Tournaments</h1>
{#each tournaments as tournament}
    <TournamentPageItem id={tournament.id} name={tournament.name} game={tournament.game} mode={tournament.mode} date_start={tournament.date_start} date_end={tournament.date_end}/>
{/each}