<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import RecentTransactions from '$lib/components/homepage/RecentTransactions.svelte';
  import LatestTournaments from '$lib/components/homepage/LatestTournaments.svelte';
  import LatestResults from '$lib/components/homepage/LatestResults.svelte';
  import NewestTeams from '$lib/components/homepage/NewestTeams.svelte';
  import NewestPlayers from '$lib/components/homepage/NewestPlayers.svelte';
  import LatestAnnouncements from '$lib/components/homepage/LatestAnnouncements.svelte';
</script>

<svelte:head>
  <title>MKCentral</title>
</svelte:head>

<div class="welcome">
  <h1 class="text-2xl font-bold mb-[20px]">{$LL.HOMEPAGE.WELCOME()}</h1>
  <p class="max-w-screen-md text-left px-[20px] md:px-0 mb-[20px]">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html $LL.HOMEPAGE.SUMMARY()}
    <a href="/{$page.params.lang}/about" class="text-green-500 hover:underline font-semibold ml-1">
      {$LL.HOMEPAGE.LEARN_MORE_ABOUT_US()}
    </a>
  </p>
</div>


<div class="grid-container">
  <LatestAnnouncements style='grid-area: f;'/>
  <LatestTournaments style='grid-area: a;' />
  <LatestResults style='grid-area: b;' />
  <NewestPlayers style='grid-area: c;' />
  <NewestTeams style='grid-area: d;' />
  <RecentTransactions style='grid-area: e;' />
</div>

<style>
  .welcome {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .welcome p {
      margin-left: auto;
      margin-right: auto;
  }

  .grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto;
    grid-template-areas: 
      "f f b"
      "a a b"
      "c d e";
    gap: 15px;
    margin: 20px 0;
  }
  
  @media (min-width: 1025px) and (max-width: 1279px) {
    .grid-container {
      grid-template-columns: repeat(2, 1fr);
      grid-template-areas: 
        "f f"
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
  @media (max-width: 600px) {
    .welcome p {
      padding: 0 20px;
    }
  }
</style>