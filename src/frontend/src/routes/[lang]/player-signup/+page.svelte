<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { FriendCode } from '$lib/types/friend-code';
  import { goto } from '$app/navigation';
  import Section from '$lib/components/common/Section.svelte';
  import CountrySelect from '$lib/components/common/CountrySelect.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LinkDiscord from '$lib/components/common/discord/LinkDiscord.svelte';

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
      friend_codes.push({ id: 0, fc: fc, game: games[i], is_primary: true, description: null, is_verified: false });
    }

    const payload = {
      name: data.get('name'),
      country_code: data.get('country'),
      friend_codes: friend_codes,
      is_hidden: false,
      is_shadow: false,
      is_banned: false,
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

{#if user_info.player_id !== null}
  Already registered
{:else}
  <Section header="Discord">
    <LinkDiscord/>
  </Section>
  <Section header="Player Signup">
    <form method="post" on:submit|preventDefault={register}>
      <div class="field">
        <span class="item-label">
          <label for="name">Name</label>
        </span>
        <input name="name" type="name" minlength="2" />
      </div>
      <div class="field">
        <span class="item-label">
          <label for="country">Country</label>
        </span>
        <CountrySelect is_required={true}/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="switch_fc">Switch FC</label>
        </span>
        <input name="switch_fc" />
      </div>
      <div class="field">
        <span class="item-label">
          <label for="mkt_fc">MKTour FC</label>
        </span>
        <input name="mkt_fc" />
      </div>
      <div class="field">
        <span class="item-label">
          <label for="mkw_fc">MKW FC</label>
        </span>
        <input name="mkw_fc" />
      </div>
      <div class="field">
        <span class="item-label">
          <label for="3ds_fc">3DS FC</label>
        </span>
        <input name="3ds_fc" />
      </div>
      <div class="field">
        <span class="item-label">
          <label for="nnid">Nintendo Network ID</label>
        </span>
        <input name="nnid" />
      </div>
      <Button type="submit">Register</Button>
    </form>
  </Section>
{/if}

<style>
  div.field {
    margin-bottom: 5px;
  }
  span.item-label {
    display: inline-block;
    width: 150px;
  }
  input {
    width: 200px;
  }
</style>