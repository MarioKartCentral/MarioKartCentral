<script lang="ts">
    import { page } from '$app/stores';

    export let id: number;
    export let name: string;
    export let game: string;
    export let mode: string;
    export let date_start: Date;
    export let date_end: Date;
    export let series_id: number;
    export let series_name: string | null;
    export let series_url: string | null;
    export let series_description: string | null;
    export let is_squad: boolean;
    export let teams_allowed: boolean;
    export let description: string;
    export let logo: string | null;

    $: tournament_type = (is_squad ? (teams_allowed ? "Team" : "Squad") : "Solo");
    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
</script>

<div class="container">
    <div>{id}</div>
    <div class="name"><h3><a href="/{$page.params.lang}/tournaments/details?id={id}">{name}</a></h3></div>
    <div>{game.toUpperCase()}</div>
    <div>{mode}</div>
    <div>{tournament_type}</div>
    <div>{months[date_start.getMonth()]} {date_start.getDate()}-{months[date_end.getMonth()]} {date_end.getDate()}</div>
    {#if logo != null}
    <div><img src={logo} alt={name}/></div>
    {/if}
    {#if series_id != null}
    <div>Series {series_id} - {series_name}</div>
    <div>{series_description}</div>
    {/if}
</div>

<style>
    .container {
        display: grid;
        background-color: rgba(24, 82, 28, 0.8);
        padding-top: 10px;
        padding-bottom: 10px;
        margin: 10px auto 10px auto;
    }
    .name {
        display: inline-block;
    }
    img {
        max-width: 400px;
        max-height: 200px;
    }
</style>