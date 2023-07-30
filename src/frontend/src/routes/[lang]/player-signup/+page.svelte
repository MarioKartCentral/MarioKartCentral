<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { FriendCode } from '$lib/types/friend-code';
  import { goto } from '$app/navigation';
  import { country_codes } from '$lib/stores/country_codes';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  async function register(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const data = new FormData(event.currentTarget);
    const fc_labels = ['switch_fc', 'mkt_fc', 'mkw_fc', '3ds_fc', 'nnid'];
    const games = ['mk8dx', 'mkt', 'mkw', 'mk7', 'mk8'];
    let friend_codes: FriendCode[] = [];
    for (let i = 0; i < fc_labels.length; i++) {
      let fc = data.get(fc_labels[i]) as string;
      if (fc === '') {
        continue;
      }
      friend_codes.push({ fc: fc, game: games[i], is_primary: true, description: null, is_verified: false });
    }

    const payload = {
      name: data.get('name'),
      country_code: data.get('country_code'),
      friend_codes: friend_codes,
      is_hidden: false,
      is_shadow: false,
      is_banned: false,
      discord_id: data.get('discord_id'),
    };
    const endpoint = '/api/registry/players/create';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.status < 300) {
      goto('/');
      alert('Registered successfully!');
    } else {
      alert(`Registration failed: ${result['title']}`);
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
      <input name="name" type="name" />
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
      <label for="switch_fc">Switch FC</label>
      <input name="switch_fc" />
    </div>
    <div>
      <label for="mkt_fc">MKTour FC</label>
      <input name="mkt_fc" />
    </div>
    <div>
      <label for="mkw_fc">MKW FC</label>
      <input name="mkw_fc" />
    </div>
    <div>
      <label for="3ds_fc">3DS FC</label>
      <input name="3ds_fc" />
    </div>
    <div>
      <label for="nnid">Nintendo Network ID</label>
      <input name="nnid" />
    </div>
    <div>
      <label for="discord_id">Discord ID</label>
      <input name="discord_id" type="discord_id" />
    </div>
    <button class="register-btn" type="submit">Register</button>
  </form>
{/if}
