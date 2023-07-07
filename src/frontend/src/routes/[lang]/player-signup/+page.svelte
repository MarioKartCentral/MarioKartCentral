<script lang="ts">
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from "$lib/types/user-info";
    import { goto } from '$app/navigation';
    import { country_codes } from "$lib/stores/country_codes";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    async function register(event: SubmitEvent & {currentTarget: EventTarget & HTMLFormElement}) {
        const data = new FormData(event.currentTarget);
        const payload = { name: data.get('name'),
                        country_code: data.get('country_code'),
                        is_hidden: false,
                        is_shadow: false,
                        is_banned: false,
                        discord_id: data.get('discord_id')
                    };
        const endpoint = "/api/registry/players/create";
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify(payload) });
        const result = await response.json();

        if (response.status < 300) {
            goto('/');
        } 
        else {
            alert("Registration failed");
        }
    }
</script>

<h2>Player Signup</h2>

{#if user_info.player_id !== null}
    Already registered
{:else}
    <form method="post" on:submit|preventDefault={register}>
        <div>
            <label for="name">Name</label>
            <input name="name" type="name">
        </div>
        <div>
            <label for="country_code">Country</label>
            <select name="country_code">
                {#each country_codes as country_code}
                    <option value={country_code}>{country_code}</option>
                {/each}
            </select>
        </div>
        <div>
            <label for="discord_id">Discord ID</label>
            <input name="discord_id" type="discord_id">
        </div>
        <button class="register-btn">Register</button>
    </form>
{/if}