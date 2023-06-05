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
        series_id: number;
        series_name: string | null;
        series_url: string | null;
        series_description: string | null;
        is_squad: boolean;
        teams_allowed: boolean;
        description: string;
        logo: string | null;

        constructor(id: number, name: string, game: string, mode: string, d_start: number, d_end: number, series_id: number, series_name: string | null,
                    series_url: string | null, series_description: string | null, is_squad: boolean, teams_allowed: boolean, description: string, 
                    logo: string | null) {
            this.id = id;
            this.name = name;
            this.game = game;
            this.mode = mode;
            this.date_start = new Date(d_start * 1000);
            this.date_end = new Date(d_end * 1000);
            this.series_id = series_id;
            this.series_name = series_name;
            this.series_url = series_url;
            this.series_description = series_description;
            this.is_squad = is_squad;
            this.teams_allowed = teams_allowed;
            this.description = description;
            this.logo = logo;
        }
    }

    onMount(async () => {
        const res = await fetch('/api/tournaments/list');
        if(res.status === 200) {
            const body = await res.json();
            for(let t of body) {
                let tournament = new Tournament(t.id, t.tournament_name, t.game, t.mode, t.date_start, t.date_end, t.series_id, t.series_name, t.series_url,
                t.series_description, t.is_squad, t.teams_allowed, t.description, t.logo);
                tournaments.push(tournament);
            }
            tournaments=tournaments;
        }
    });
</script>

<h1>Tournaments</h1>
{#each tournaments as tournament}
    <TournamentPageItem id={tournament.id} name={tournament.name} game={tournament.game} mode={tournament.mode} date_start={tournament.date_start} date_end={tournament.date_end}
    series_id={tournament.series_id} series_name={tournament.series_name} series_url={tournament.series_url} series_description={tournament.series_description}
    is_squad={tournament.is_squad} teams_allowed={tournament.teams_allowed} description={tournament.description} logo={tournament.logo}/>
{/each}