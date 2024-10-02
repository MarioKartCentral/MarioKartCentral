<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
    import Button from '$lib/components/common/buttons/Button.svelte';
  export let userId = 'Loading...';
  export let playerId = '';
  export let isLoggedIn = false;
  import LoginRegister from '$lib/components/common/LoginRegister.svelte';

  onMount(async () => {
    const res = await fetch(`/api/user/me`);
    if (res.status === 200) {
      const body = await res.json();
      userId = body['id'];
      playerId = body['player_id'] || 'User has not completed player registration';
      isLoggedIn = true;
    } else {
      userId = 'Not logged in';
      playerId = 'N/A';
      isLoggedIn = false;
    }
  });

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async function logout(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
    const response = await fetch('/api/user/logout', { method: 'POST' });

    if (response.status < 300) {
      goto('/');
    } else {
      alert('Logout failed');
    }
  }
</script>

<svelte:head>
  <title>Mario Kart Central</title>
</svelte:head>

<h1>{$LL.WELCOME()}</h1>
<p>{$LL.SUMMARY()}</p>
<p>{$LL.PLAYER_PROFILE.LANGUAGE()}: {$LL.LANGUAGE()}</p>

<p>User ID: {userId}</p>
<p>Player ID: {playerId}</p>
{#if isLoggedIn}
  <form method="post" on:submit|preventDefault={logout}>
    <Button type="submit">{$LL.LOGOUT()}</Button>
  </form>
{:else}
  <LoginRegister/>
{/if}
