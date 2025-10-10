<script lang="ts">
  import type { APIToken } from '$lib/types/api-tokens';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';

  export let token: APIToken;
  export let is_privileged = false;

  async function delete_token() {
    let conf = window.confirm($LL.API_TOKENS.DELETE_TOKEN_CONFIRM({ name: token.name }));
    if (!conf) return;
    const endpoint = is_privileged ? `/api/user/${token.user_id}/delete_api_token` : '/api/user/delete_api_token';
    const payload = {
      token_id: token.token_id,
    };
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (response.status < 300) {
      window.location.reload();
    } else {
      const result = await response.json();
      alert(`${$LL.API_TOKENS.DELETE_TOKEN_FAILED()}: ${result['title']}`);
    }
  }

  let show_token = false;
</script>

<div class="mb-5">
  <div class="flex gap-2 items-center mb-2">
    <div>
      {$LL.API_TOKENS.TOKEN_NAME()}
    </div>
    <div class="name">
      {token.name}
    </div>
    <div>
      <Button on:click={() => (show_token = !show_token)}>
        {#if show_token}
          {$LL.COMMON.HIDE()}
        {:else}
          {$LL.COMMON.SHOW()}
        {/if}
      </Button>
    </div>

    <div>
      <Button on:click={delete_token}>
        {$LL.COMMON.DELETE()}
      </Button>
    </div>
  </div>
  {#if show_token}
    <div>
      {token.token_id}
    </div>
  {/if}
</div>

<style>
  .name {
    width: 150px;
  }
</style>
