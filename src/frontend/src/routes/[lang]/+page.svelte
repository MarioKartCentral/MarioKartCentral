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

<div class="home-row">
  <div class="latest-tournament">
    <LatestTournaments />
  </div>
  <div class="latest-results">
    <LatestResults />
  </div>
</div>
<div class="home-row">
  <NewestPlayers />
  <NewestTeams />
  <RecentTransactions />
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
  .home-row {
    display: flex;
    gap: 15px;
  }
  .latest-tournament {
    flex: 2;
  }
  .latest-results {
    flex: 1;
  }
</style>