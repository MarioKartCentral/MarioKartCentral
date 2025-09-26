<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';

  export let email = '';
  export let password = '';
  export let old_password = '';
  export let is_change = false;
  export let is_reset = false;
  export let working = false;

  const min_length = 8;

  let confirm_password = '';
  let agree_terms = false;
  let agree_policy = false;

  $: button_disabled =
    password.length < 8 || password != confirm_password || (!is_change && !is_reset && (!agree_terms || !agree_policy));
</script>

<div class="form">
  <form on:submit|preventDefault>
    {#if !is_change}
      <div class="option">
        <span class="item-label">
          <label for="email">{$LL.LOGIN.EMAIL()}</label>
        </span>
        <input name="email" type="email" bind:value={email} disabled={is_reset} required />
      </div>
    {/if}
    {#if is_change}
      <div class="option">
        <span class="item-label">
          <label for="old-password">
            {$LL.LOGIN.OLD_PASSWORD()}
          </label>
        </span>
        <input name="old-password" type="password" bind:value={old_password} />
      </div>
    {/if}
    <div class="option">
      <span class="item-label">
        <label for="password">
          {#if is_reset}
            {$LL.LOGIN.NEW_PASSWORD()}
          {:else}
            {$LL.LOGIN.PASSWORD()}
          {/if}
        </label>
      </span>
      <input name="password" type="password" minlength={min_length} maxlength="64" bind:value={password} required />
    </div>
    <div class="option">
      <span class="item-label">
        <label for="confirm-password">{$LL.LOGIN.CONFIRM_PASSWORD()}</label>
      </span>
      <input
        name="confirm-password"
        type="password"
        minlength={min_length}
        maxlength="64"
        bind:value={confirm_password}
        required
      />
    </div>
    {#if !is_change && !is_reset}
      <div class="option">
        <span class="agree-terms">
          <input name="terms" type="checkbox" bind:checked={agree_terms} />
        </span>
        <div class="terms-label">
          <a href="/{$page.params.lang}/user/terms" target="_blank">
            {$LL.LOGIN.AGREE_TO_TERMS()}
          </a>
        </div>
      </div>
      <div class="option">
        <span class="agree-terms">
          <input name="privacy" type="checkbox" bind:checked={agree_policy} />
        </span>
        <div class="terms-label">
          <a href="/{$page.params.lang}/user/privacy-policy" target="_blank">
            {$LL.LOGIN.AGREE_TO_PRIVACY_POLICY()}
          </a>
        </div>
      </div>
    {/if}
    <div class="errors">
      {#if password.length && password.length < min_length}
        <div>
          {$LL.LOGIN.PASSWORD_CHARACTER_WARNING({ count: min_length })}
        </div>
      {/if}
      {#if password !== confirm_password}
        <div>
          {$LL.LOGIN.PASSWORD_NO_MATCH()}
        </div>
      {/if}
    </div>
    <div>
      <Button type="submit" disabled={button_disabled} {working}>
        {#if is_change}
          {$LL.LOGIN.CHANGE_PASSWORD()}
        {:else if is_reset}
          {$LL.LOGIN.RESET_PASSWORD()}
        {:else}
          {$LL.LOGIN.REGISTER()}
        {/if}
      </Button>
    </div>
  </form>
</div>

<style>
  .form {
    max-width: 350px;
  }
  span.item-label {
    display: inline-block;
    width: 150px;
  }
  .option {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 10px;
  }
  .errors {
    color: #ffcccb;
    margin-left: 5px;
    margin-bottom: 10px;
  }
  span.agree-terms {
    margin-right: 10px;
  }
  .terms-label {
    text-decoration: underline;
  }
</style>
