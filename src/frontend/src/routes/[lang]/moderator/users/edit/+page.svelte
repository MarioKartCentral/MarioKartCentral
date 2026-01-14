<script lang="ts">
  import { onMount } from 'svelte';
  import type { UserDetailed } from '$lib/types/user';
  import { page } from '$app/stores';
  import Section from '$lib/components/common/Section.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import DiscordDisplay from '$lib/components/common/discord/DiscordDisplay.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_permission, permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';
  import ApiTokenDisplay from '$lib/components/user/APITokenDisplay.svelte';

  let id: number | null = null;
  let user_found = true;
  let edit_user: UserDetailed;
  let change_password = false;
  let new_password = '';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    let param_id = $page.url.searchParams.get('id');
    id = Number(param_id);
    const res = await fetch(`/api/user/${id}`);
    if (res.status !== 200) {
      user_found = false;
      return;
    }
    const body: UserDetailed = await res.json();
    edit_user = body;
  });

  async function editUser() {
    const payload = {
      user_id: id,
      email: edit_user.email,
      password: change_password ? new_password : null,
      email_confirmed: edit_user.email_confirmed,
      force_password_reset: edit_user.force_password_reset,
    };
    console.log(payload);
    const endpoint = '/api/user/edit';
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.MANAGE_USERS.EDIT_USER_FAILED()}: ${result['title']}`);
    }
  }

  let token_name = '';
  let working = false;
  async function createToken() {
    working = true;
    const payload = {
      name: token_name,
    };
    const endpoint = `/api/user/${edit_user.id}/create_api_token`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.API_TOKENS.CREATE_TOKEN_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if check_permission(user_info, permissions.edit_user)}
  {#if edit_user}
    <Section header={$LL.MODERATOR.MANAGE_USERS.BACK_TO_USER_LIST()}>
      <div slot="header_content">
        <Button href="/{$page.params.lang}/moderator/users">{$LL.COMMON.BACK()}</Button>
      </div>
    </Section>
    <Section header={$LL.MODERATOR.MANAGE_USERS.EDIT_USER_HEADER({ user_id: edit_user.id })}>
      <form on:submit|preventDefault={editUser}>
        <div class="option">
          <div class="label">
            <label for="email">{$LL.LOGIN.EMAIL()}</label>
          </div>
          <div>
            <input type="email" bind:value={edit_user.email} required />
          </div>
        </div>
        <div class="option">
          <div class="label">
            <label for="email_confirmed">{$LL.MODERATOR.MANAGE_USERS.EMAIL_CONFIRMED()}</label>
          </div>
          <div>
            <select name="email_confirmed" bind:value={edit_user.email_confirmed}>
              <option value={true}>{$LL.MODERATOR.MANAGE_USERS.EMAIL_CONFIRMED_TRUE()}</option>
              <option value={false}>{$LL.MODERATOR.MANAGE_USERS.EMAIL_CONFIRMED_FALSE()}</option>
            </select>
          </div>
        </div>
        <div class="option">
          <div class="label">
            <label for="force_password_reset">{$LL.MODERATOR.MANAGE_USERS.FORCE_PASSWORD_RESET()}</label>
          </div>
          <div>
            <select name="force_password_reset" bind:value={edit_user.force_password_reset}>
              <option value={false}>{$LL.MODERATOR.MANAGE_USERS.FORCE_PASSWORD_RESET_FALSE()}</option>
              <option value={true}>{$LL.MODERATOR.MANAGE_USERS.FORCE_PASSWORD_RESET_TRUE()}</option>
            </select>
          </div>
        </div>
        <div class="option">
          <div class="label">
            <label for="change_password">
              {$LL.LOGIN.PASSWORD()}
            </label>
          </div>
          <div>
            <select bind:value={change_password} name="change_password">
              <option value={false}>{$LL.MODERATOR.MANAGE_USERS.DO_NOT_CHANGE_PASSWORD()}</option>
              <option value={true}>{$LL.MODERATOR.MANAGE_USERS.SET_NEW_PASSWORD()}</option>
            </select>
            {#if change_password}
              <div class="change_password">
                <input
                  type="password"
                  bind:value={new_password}
                  placeholder={$LL.MODERATOR.MANAGE_USERS.NEW_PASSWORD()}
                  required
                />
              </div>
            {/if}
          </div>
        </div>
        <div class="option">
          <div class="label">
            {$LL.COMMON.PLAYER()}
          </div>
          <div>
            {#if edit_user.player}
              <a href="/{$page.params.lang}/registry/players/profile?id={edit_user.player.id}">
                <div class="flex">
                  <div>
                    <Flag country_code={edit_user.player.country_code} />
                  </div>
                  <div>
                    {edit_user.player.name}
                  </div>
                </div>
              </a>
            {:else}
              {$LL.MODERATOR.MANAGE_USERS.USER_NO_PLAYER()}
            {/if}
          </div>
        </div>
        <div class="option">
          <div class="label">{$LL.DISCORD.DISCORD()}</div>
          <div>
            {#if edit_user.player?.discord}
              <DiscordDisplay discord={edit_user.player.discord} enableUserIdToggle />
            {:else}
              {$LL.MODERATOR.MANAGE_USERS.USER_NO_DISCORD()}
            {/if}
          </div>
        </div>
        <div>
          <Button type="submit">{$LL.COMMON.SAVE()}</Button>
        </div>
      </form>
    </Section>
    <Section header={$LL.API_TOKENS.API_TOKENS()}>
      <div class="flex gap-2 mb-5">
        <input class="token-name" bind:value={token_name} placeholder={$LL.API_TOKENS.TOKEN_NAME_HERE()} />
        <Button on:click={createToken} disabled={!token_name.length} {working}>{$LL.API_TOKENS.CREATE_TOKEN()}</Button>
      </div>
      {#each edit_user.tokens as token (token.token_id)}
        <ApiTokenDisplay {token} is_privileged={true} />
      {/each}
    </Section>
  {:else if !user_found}
    {$LL.MODERATOR.MANAGE_USERS.USER_NOT_FOUND()}
  {/if}
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}

<style>
  div.option {
    margin-bottom: 10px;
    display: flex;
    align-items: center;
  }
  div.label {
    width: 200px;
  }
  div.flex {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  div.change_password {
    margin-top: 10px;
  }
  input.token-name {
    width: 250px;
  }
</style>
