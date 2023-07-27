<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { UserSettings } from '$lib/types/user-settings';
  import type { FriendCode } from '$lib/types/friend-code';

  let user_info: UserInfo;
  let user_settings: UserSettings | null;
  const languages = ['de', 'en-gb', 'en-us', 'es', 'fr', 'ja'];
  const color_schemes = ['light', 'dark'];
  const timezones = ['utc'];
  const games = ['mk8dx', 'mkt', 'mkw', 'mk7', 'mk8'];
  // how many friend codes a player can have per game
  const fc_limits: { [key: string]: number } = { mk8dx: 1, mkt: 1, mkw: 4, mk7: 1, mk8: 1 };
  const fc_form_visible: { [key: string]: boolean } = { mk8dx: false, mkt: false, mk7: false, mk8: false };
  user.subscribe((value) => {
    user_info = value;
  });

  $: player = user_info.player ? user_info.player : null;
  $: user_settings = player?.user_settings ? player.user_settings : null;

  // get an object containing the list of friend codes for each game
  function fc_games(fcs: FriendCode[]) {
    let grouped_fcs: { [key: string]: FriendCode[] } = {};
    for (const game of games) {
      grouped_fcs[game] = fcs.filter((fc) => fc.game === game);
    }
    return grouped_fcs;
  }

  function toggle_fc_form(game: string) {
    fc_form_visible[game] = !fc_form_visible[game];
  }

  async function editProfile(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    const payload = {
      avatar: data.get('avatar_url')!.toString(),
      about_me: data.get('about_me')!.toString(),
      language: data.get('language')!.toString(),
      color_scheme: data.get('theme')!.toString(),
      timezone: data.get('timezone')!.toString(),
    };
    const endpoint = '/api/user/settings/edit';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.status < 300) {
      goto(`/${$page.params.lang}/registry/players/profile?id=${user_info.player_id}`);
      alert('Edited profile successfully');
    } else {
      alert(`Editing profile failed: ${result['title']}`);
    }
  }

  async function addFC(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    const payload = {
      fc: data.get('fc')!.toString(),
      game: data.get('game')!.toString(),
      is_primary: data.get('is_primary') ? true : false,
      description: data.get('description')!.toString(),
    };
    const endpoint = '/api/registry/addFriendCode';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.status < 300) {
      goto(`/${$page.params.lang}/registry/players/profile?id=${user_info.player_id}`);
      alert('Added friend code successfully');
    } else {
      alert(`Adding friend code failed: ${result['title']}`);
    }
  }
</script>

<svelte:head>
  <title>Edit Profile | Mario Kart Central</title>
</svelte:head>

<div class="container">
  {#if player}
    <h2>Friend Codes</h2>
    {#each Object.entries(fc_games(player.friend_codes)) as [game, fcs]}
      <h3>{game}</h3>
      {#each fcs as fc}
        <div>{fc.fc}</div>
      {/each}
      {#if fcs.length < fc_limits[game]}
        <button on:click={() => toggle_fc_form(game)}>Add Friend Code</button>
      {/if}
      {#if fc_form_visible[game]}
        <form method="post" on:submit|preventDefault={addFC}>
          <div>
            <label for="fc">Friend Code</label>
            <input name="fc" placeholder={game !== 'mk8' ? '0000-0000-0000' : ''} />
            <label for="is_primary">Primary?</label>
            <input name="is_primary" type="checkbox" />
            <input name="description" placeholder="Description" />
            <input type="hidden" name="game" value={game} />
            <button type="submit">Submit</button>
          </div>
        </form>
      {/if}
    {/each}
  {/if}
  <h2>Edit Profile</h2>
  <form method="post" on:submit|preventDefault={editProfile}>
    <div>
      <label for="avatar_url">Avatar URL</label>
      <br />
      <input name="avatar_url" type="text" value={user_settings?.avatar ? user_settings.avatar : ''} />
    </div>
    <div>
      <label for="about_me">About Me</label>
      <br />
      <textarea name="about_me">{user_settings?.about_me ? user_settings.about_me : ''}</textarea>
    </div>
    <div>
      <label for="language">Language</label>
      <br />
      <select name="language">
        {#each languages as language}
          <option value={language}>{language}</option>
        {/each}
      </select>
    </div>
    <div>
      <label for="theme">Theme</label>
      <br />
      <select name="theme">
        {#each color_schemes as theme}
          <option value={theme}>{theme}</option>
        {/each}
      </select>
    </div>
    <div>
      <label for="timezone">Timezone</label>
      <br />
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
