<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from "$lib/types/user-info";
    import type { UserSettings } from "$lib/types/user-settings";

    let user_info: UserInfo;
    let user_settings: UserSettings | null;
    let languages = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];
    let color_schemes = ['light', 'dark'];
    let timezones = ['utc'];

    user.subscribe((value) => {
        user_info = value;
    });

    $: user_settings = user_info.player?.user_settings ? user_info.player.user_settings : null;

    async function editProfile(event: SubmitEvent & {currentTarget: EventTarget & HTMLFormElement}) {
        const data = new FormData(event.currentTarget);
        const payload = {   avatar: data.get("avatar_url")!.toString(), 
                            about_me: data.get("about_me")!.toString(),
                            language: data.get("language")!.toString(),
                            color_scheme: data.get("theme")!.toString(),
                            timezone: data.get("timezone")!.toString()
                        };
        const endpoint = "/api/user/settings/edit";
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify(payload) });
        const result = await response.json();

        if (response.status < 300) {
            goto(`/${$page.params.lang}/registry/players/profile?id=${user_info.player_id}`);
            alert("Edited profile successfully");
        } 
        else {
            alert(`Editing profile failed: ${result['title']}`);
        }
    }

</script>

<svelte:head>
    <title>Edit Profile | Mario Kart Central</title>
</svelte:head>

<div class="container">
    <h2>Edit Profile</h2>
    <form method="post" on:submit|preventDefault={editProfile}>
        <div>
            <label for="avatar_url">Avatar URL</label>
            <br>
            <input name="avatar_url" type="text" value={user_settings?.avatar ? user_settings.avatar : ""}>
        </div>
        <div>
            <label for="about_me">About Me</label>
            <br>
            <textarea name="about_me">{user_settings?.about_me ? user_settings.about_me : ""}</textarea>
        </div>
        <div>
            <label for="language">Language</label>
            <br>
            <select name="language">
                {#each languages as language}
                    <option value={language}>{language}</option>
                {/each}
            </select>
        </div>
        <div>
            <label for="theme">Theme</label>
            <br>
            <select name="theme">
                {#each color_schemes as theme}
                    <option value={theme}>{theme}</option>
                {/each}
            </select>
        </div>
        <div>
            <label for="timezone">Timezone</label>
            <br>
            <select name="timezone">
                {#each timezones as tz}
                    <option value={tz}>{tz}</option>
                {/each}
            </select>
        </div>
        <button type="submit">Save</button>
    </form>
</div>

<style>
    .container {
        width: 50%;
        margin: 20px auto 20px auto;
    }
</style>