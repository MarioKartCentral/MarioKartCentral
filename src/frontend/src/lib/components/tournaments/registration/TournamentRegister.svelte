<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import Section from "$lib/components/common/Section.svelte";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { page } from "$app/stores";
    import type { FriendCode } from "$lib/types/friend-code";

    export let tournament: Tournament;

    let user_info: UserInfo;
    user.subscribe((value) => {
        user_info = value;
    });

    function get_game_fcs(game: string, fcs: FriendCode[]) {
        return fcs.filter((fc) => fc.game === game);
    }
</script>

<Section header="Register">
    {#if user_info.player}
        <div>
            Want to register for this tournament? Just fill out your registration details below!
        </div>
        
            {#if get_game_fcs(tournament.game, user_info.player.friend_codes).length}
                <form method="POST">
                    {#if tournament.require_single_fc}
                        <label for="selected_fc_id">Select FC</label>
                        <select name="selected_fc_id">
                            {#each get_game_fcs(tournament.game, user_info.player.friend_codes) as fc}
                                <option value={fc.id}>{fc.fc}</option>
                            {/each}
                        </select>
                    {/if}
                </form>
            {:else}
                <div>Please add an FC for {tournament.game} to register for this tournament.</div>
            {/if}
        
    {:else}
        <div><a href="/{$page.params.lang}/player-signup">Please complete your player registration to register for this tournament.</a></div>
    {/if}
</Section>