<script lang="ts">
    export let id: Number;
    export let name: string;
    export let game: string;
    export let mode: string;
    export let date_start: Date;
    export let date_end: Date;

    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
</script>

<div class="container">
    <div>{id}</div>
    <div class="name"><h3>{name}</h3></div>
    <div>{game.toUpperCase()}</div>
    <div>{mode}</div>
    <div>{months[date_start.getMonth()]} {date_start.getDate()}-{months[date_end.getMonth()]} {date_end.getDate()}</div>
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
</style>