<script lang="ts">
    import GameSelect from "$lib/components/common/GameSelect.svelte";
    import LL from "$i18n/i18n-svelte";
    import type { PlayerInfo } from "$lib/types/player-info";
    import Button from "$lib/components/common/buttons/Button.svelte";

    export let player: PlayerInfo | null;
    let selected_game: string | null = null;

    const fc_limits: { [key: string]: number } = { mk8dx: 1, mkt: 1, mkw: 4, mk7: 1, mk8: 1 };

    function get_maxed_games() {
        if(!player) return [];
        // get all games where we have reached the FC limit
        let maxed_games = Object.keys(fc_limits).filter(
            (game) => player.friend_codes.filter((fc) => fc.game === game).length >= fc_limits[game]
        );
        maxed_games.push('smk'); // smk is on switch so should use mk8dx fcs for that
        console.log(maxed_games);
        return maxed_games;
    }

    async function addFC(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const data = new FormData(event.currentTarget);
        const payload = {
            fc: data.get('fc')?.toString(),
            game: data.get('game')?.toString(),
            is_primary: data.get('is_primary') ? true : false,
            description: data.get('description')?.toString(),
        };
        console.log(payload);
        const endpoint = '/api/registry/addFriendCode';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Adding friend code failed: ${result['title']}`);
        }
    }
</script>

{#if player}
    <form method="post" on:submit|preventDefault={addFC}>
        <div>
            <div class="option">
                <GameSelect bind:game={selected_game} flex required disabled_games={get_maxed_games()}/>
            </div>
            <div class="option">
            <div>
                <label for="fc">{$LL.PLAYER_PROFILE.FRIEND_CODE()}</label>
            </div>
            <div>
                <input name="fc" placeholder={selected_game !== 'mk8' ? '0000-0000-0000' : 'NNID'} 
                minlength={selected_game === 'mk8' ? 6 : null} maxlength={selected_game === 'mk8' ? 16 : null} 
                required/>
            </div>
            </div>
            <div class="option">
            <div>
                <label for="is_primary">{$LL.PLAYER_PROFILE.PRIMARY()}</label>
            </div>
            <div>
                <input name="is_primary" type="checkbox" />
            </div>
            </div>
            <div class="option">
            <div>
                <label for="description">{$LL.PLAYER_PROFILE.DESCRIPTION()}</label>
            </div>
            <div>
                <input name="description" placeholder={$LL.PLAYER_PROFILE.DESCRIPTION()} />
            </div>
            </div>
            <Button type="submit">{$LL.PLAYER_PROFILE.SUBMIT()}</Button>
        </div>
    </form>
{/if}

<style>
    :global(label) {
        display: inline-block;
        width: 100px;
        margin-right: 10px;
    }
    input {
        width: 200px;
    }
    input[type=checkbox] {
        width: 15px;
    }
    .option {
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
</style>