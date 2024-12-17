<script lang="ts">
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { FriendCode } from '$lib/types/friend-code';
  import { goto } from '$app/navigation';
  import Section from '$lib/components/common/Section.svelte';
  import CountrySelect from '$lib/components/common/CountrySelect.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LinkDiscord from '$lib/components/common/discord/LinkDiscord.svelte';
  import LL from '$i18n/i18n-svelte';

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
      friend_codes.push({ id: 0, fc: fc.replaceAll(" ", "-"), game: games[i], is_primary: true, description: null, is_verified: false, is_active: true });
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
      alert($LL.PLAYERS.PLAYER_SIGNUP.REGISTER_SUCCESS());
    } else {
      alert(`${$LL.PLAYERS.PLAYER_SIGNUP.REGISTER_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if user_info.player_id !== null}
  {$LL.PLAYERS.PLAYER_SIGNUP.ALREADY_REGISTERED()}
{:else}
  <Section header={$LL.DISCORD.DISCORD()}>
    <LinkDiscord/>
  </Section>
  <Section header={$LL.PLAYERS.PLAYER_SIGNUP.PLAYER_SIGNUP()}>
    <form method="post" on:submit|preventDefault={register}>
      <div class="field">
        <span class="item-label">
          <label for="name">{$LL.COMMON.NAME()}</label>
        </span>
        <input name="name" type="name" minlength="2" pattern="^\S.*\S$|^\S$" />
      </div>
      <div class="field">
        <span class="item-label">
          <label for="country">{$LL.COMMON.COUNTRY()}</label>
        </span>
        <CountrySelect is_required={true}/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="switch_fc">{$LL.PLAYERS.PLAYER_SIGNUP.SWITCH_FC()}</label>
        </span>
        <input name="switch_fc" placeholder='0000-0000-0000'/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="mkt_fc">{$LL.PLAYERS.PLAYER_SIGNUP.MKT_FC()}</label>
        </span>
        <input name="mkt_fc" placeholder='0000-0000-0000'/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="mkw_fc">{$LL.PLAYERS.PLAYER_SIGNUP.MKW_FC()}</label>
        </span>
        <input name="mkw_fc" placeholder='0000-0000-0000'/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="3ds_fc">{$LL.PLAYERS.PLAYER_SIGNUP['3DS_FC']()}</label>
        </span>
        <input name="3ds_fc" placeholder='0000-0000-0000'/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="nnid">{$LL.PLAYERS.PLAYER_SIGNUP.NNID()}</label>
        </span>
        <input name="nnid" placeholder='NNID'/>
      </div>
      <Button type="submit">{$LL.PLAYERS.PLAYER_SIGNUP.REGISTER()}</Button>
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