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
  import Input from '$lib/components/common/Input.svelte';
  import FcInput from '$lib/components/common/FCInput.svelte';

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  let working = false;

  async function register(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    working = true;
    const data = new FormData(event.currentTarget);
    const fc_labels = ['switch_fc', 'mkt_fc', 'mkw_fc', '3ds_fc', 'nnid'];
    const types = ['switch', 'mkt', 'mkw', '3ds', 'nnid'];
    let friend_codes: FriendCode[] = [];
    for (let i = 0; i < fc_labels.length; i++) {
      let fc = data.get(fc_labels[i]) as string;
      if (fc === '') {
        continue;
      }
      friend_codes.push({ id: 0, fc: fc.replaceAll(" ", "-"), type: types[i], is_primary: true, description: null, is_verified: false, is_active: true, creation_date: 0 });
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
    working = false;
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
{:else if user_info.id === null}
  {$LL.COMMON.LOGIN_REQUIRED()}
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
        <Input name="name" type="name" minlength={2} maxlength={24} no_white_space />
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
        <FcInput name="switch_fc" selected_type="switch"/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="mkt_fc">{$LL.PLAYERS.PLAYER_SIGNUP.MKT_FC()}</label>
        </span>
        <FcInput name="mkt_fc" selected_type="mkt"/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="mkw_fc">{$LL.PLAYERS.PLAYER_SIGNUP.MKW_FC()}</label>
        </span>
        <FcInput name="mkw_fc" selected_type="mkw"/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="3ds_fc">{$LL.PLAYERS.PLAYER_SIGNUP['3DS_FC']()}</label>
        </span>
        <FcInput name="3ds_fc" selected_type="3ds"/>
      </div>
      <div class="field">
        <span class="item-label">
          <label for="nnid">{$LL.PLAYERS.PLAYER_SIGNUP.NNID()}</label>
        </span>
        <FcInput name="nnid" selected_type="nnid"/>
      </div>
      <Button type="submit" {working}>{$LL.PLAYERS.PLAYER_SIGNUP.REGISTER()}</Button>
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
</style>