<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/common/buttons/Button.svelte';
  export let userId = 'Loading...';
  export let playerId = '';
  export let isLoggedIn = false;
  import LoginRegister from '$lib/components/common/LoginRegister.svelte';
  import RecentTransactions from '$lib/components/homepage/RecentTransactions.svelte';
  import LatestTournaments from '$lib/components/homepage/LatestTournaments.svelte';
  import LatestResults from '$lib/components/homepage/LatestResults.svelte';
  import NewestTeams from '$lib/components/homepage/NewestTeams.svelte';
  import NewestPlayers from '$lib/components/homepage/NewestPlayers.svelte';

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
      alert($LL.LOGIN.LOGOUT_FAILED());
    }
  }
</script>

<svelte:head>
  <title>Mario Kart Central</title>
</svelte:head>

<h1>{$LL.HOMEPAGE.WELCOME()}</h1>
<p>{$LL.HOMEPAGE.SUMMARY()}</p>

<div class="grid-container">
  <LatestTournaments style='grid-area: a;' />
  <LatestResults style='grid-area: b;' />
  <NewestPlayers style='grid-area: c;' />
  <NewestTeams style='grid-area: d;' />
  <RecentTransactions style='grid-area: e;' />
</div>


<!-- TODO: remove below -->
<p>{$LL.COMMON.LANGUAGE()}: {$LL.LANGUAGE()}</p>

<p>User ID: {userId}</p>
<p>Player ID: {playerId}</p>
{#if isLoggedIn}
  <form method="post" on:submit|preventDefault={logout}>
    <Button type="submit">{$LL.LOGIN.LOGOUT()}</Button>
  </form>
{:else}
  <LoginRegister/>
{/if}

<style>
  .grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto;
    grid-template-areas: 
      "a a b"
      "c d e";
    gap: 15px;
    margin: 20px 0;
  }
  
  @media (min-width: 1025px) and (max-width: 1279px) {
    .grid-container {
      grid-template-columns: repeat(2, 1fr);
      grid-template-areas: 
        "a a"
        "b c"
        "d e";
    }
  }
  @media (max-width: 1024px) {
    .grid-container {
      display: flex;
      flex-direction: column;
    }
  }

</style>