<script lang="ts">
    import { user } from '$lib/stores/stores';
    import type { PlayerInfo } from "$lib/types/player-info";
    import type { UserInfo } from "$lib/types/user-info";
    import logo from '$lib/assets/logo.png';

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    export let player: PlayerInfo;

    let avatar_url = logo;
    if(player.user_settings && player.user_settings.avatar) {
        avatar_url = player.user_settings.avatar;
    }
</script>
<div class="container">
    <div class="header">
        <div class="header_element"><h2>Player Profile</h2></div>
        {#if user_info.player_id == player.id}
            <div class="header_element"><button>Edit Profile</button></div>
        {/if}
    </div>
    <div class="wrapper">
        <div>
            <img class="avatar" src={avatar_url} alt={player.name}>
        </div>
        
        <div class="user_details">
            <div class="name">
                {player.name}
            </div>
            <div>
                <b>Country:</b> {player.country_code}
            </div>
            {#if player.friend_codes.length > 0}
                <div>
                    <b>Friend Codes:</b>
                    {#each player.friend_codes as fc}
                        <div class="fc">
                            {fc.fc} ({fc.game.toUpperCase()})
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
        {#if player.user_settings && player.user_settings.about_me}
            <div class="about_me">
                {player.user_settings.about_me}
            </div>
        {/if}
    </div>
</div>


<style>
    div.container {
        margin: 10px 0;
    }
    div.header {
        display: grid;
        grid-template-columns: 3fr 1fr;
        background-color: green;
    }
    div.header_element {
        margin: 5px;
    }
    div.wrapper {
        display: inline-grid;
        column-gap: 20px;
        margin: 10px 0;
        grid-template-columns: 1fr 2fr 2fr;
    }
    div.user_details {
        grid-column-start: 2;
    }
    div.name {
        font-size: 1.5em;
    }
    div.about_me {
        grid-column-start: 3;
    }
    div.fc {
        text-indent: 2em;
    }
    img.avatar {
        width: 150px;
        height: 150px;
        margin: 10px;
        border: 5px white solid;
        border-radius: 50%;
        object-fit: contain;
    }
</style>