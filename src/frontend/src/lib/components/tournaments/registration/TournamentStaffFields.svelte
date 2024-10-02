<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import type { TournamentPlayer } from "$lib/types/tournament-player";

    export let tournament: Tournament;
    export let player: TournamentPlayer | null = null;
    export let squad_exists: boolean = false;
</script>

{#if tournament.is_squad}
    {#if squad_exists}
        <div class="item">
            <span class="item-label">
                <label for="is_squad_captain">Squad captain?</label>
            </span>
            <select name="is_squad_captain" value={Boolean(player?.is_squad_captain)} required>
                <option value={false}>No</option>
                <option value={true}>Yes</option>
            </select>
        </div>
        {#if tournament.teams_only}
            <div class="item">
                <span class="item-label">
                    <label for="is_representative">Team representative?</label>
                </span>
                <select name="is_representative" value={Boolean(player?.is_representative)} required>
                    <option value={false}>No</option>
                    <option value={true}>Yes</option>
                </select>
            </div>
        {/if}
    {/if}
    {#if tournament.bagger_clause_enabled}
        <div class="item">
            <span class="item-label">
                <label for="is_bagger_clause">Bagging clause?</label>
            </span>
            <select name="is_bagger_clause" value={Boolean(player?.is_bagger_clause)} required>
                <option value={false}>No</option>
                <option value={true}>Yes</option>
            </select>
        </div>
    {/if}
{/if}
{#if tournament.checkins_enabled}
    <div class="item">
        <span class="item-label">
            <label for="is_checked_in">Checked in?</label>
        </span>
        <select name="is_checked_in" value={Boolean(player?.is_checked_in)} required>
            <option value={false}>No</option>
            <option value={true}>Yes</option>
        </select>
    </div>
{/if}
{#if tournament.verification_required && !tournament.is_squad}
    <div class="item">
        <span class="item-label">
            <label for="is_approved">Approved?</label>
        </span>
        <select name="is_approved" value={Boolean(player?.is_approved)} required>
            <option value={false}>No</option>
            <option value={true}>Yes</option>
        </select>
    </div>
{/if}

<style>
    .item-label {
        display: inline-block;
        width: 150px;
        font-weight: 525;
    }
    .item {
        margin: 10px 0;
    }
</style>