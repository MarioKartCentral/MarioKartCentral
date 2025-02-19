<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import { DiscordSolid, LinkSolid } from 'flowbite-svelte-icons';
</script>

<p>
  This page is currently a work in progress. For now,
  players can find leaderboards on several other sites.
</p>

<!--
  This page is currently a work in progress, but it will eventually be the hub for everything time trials. For now,
  players can find leaderboards on several other sites. This is the hub of Mario Kart Time Trials. Here, you'll find
  the most up-to-date rankings for Mario Kart 8 Deluxe, Mario Kart 8, Mario Kart 7, and Mario Kart Wii, with every
  category imagineable. Submit your times to see where you stack up!
-->

<main class="container">
  <GameBadge game= "mk8dx" />
  <GameBadge game= "mk7" />
  <GameBadge game= "mkw" />
  <Section header={'MKLeaderboards'}>
    <div class="flex flex-row">
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://mkleaderboards.com"><LinkSolid class="mr-2" />Website</Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/NHrtWQq">
            <DiscordSolid class="mr-2" />Discord </Button
          >
        </div>
      </div>
    </div>
  </Section>
  <GameBadge game= "mk8dx" />
  <GameBadge game = "mk8" />
  <GameBadge game= "mk7" />
  <GameBadge game= "mkw" />
  <GameBadge game= "mkds" />
  <GameBadge game= "mkdd" />
  <GameBadge game= "mksc" />
  <GameBadge game= "mk64" />
  <GameBadge game= "smk" />
  <Section header={'MKWRS'}>
    <div class="flex flex-row">
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://mkwrs.com"><LinkSolid class="mr-2" />Website</Button>
        </div>
      </div>
    </div>
  </Section>
  <GameBadge game= "mk8dx" />
  <Section header={'DLC Leaderboards'}>
    <div class="flex flex-row">
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://docs.google.com/spreadsheets/u/1/d/e/2PACX-1vRBvEljx9c5cRI-c1XMFWvkRAjeDPZK3fQwEbDADqK0XyK6RWWiZniN_5ea8RoWxzK7p-6XthRF481z/pubhtml?pli=1"><LinkSolid class="mr-2" />Website</Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/NHrtWQq">
            <DiscordSolid class="mr-2" />Discord </Button
          >
      </div>
    </div>
  </Section>
  <GameBadge game= "mk8dx" />
  <Section header={'No Item Leaderboards'}>
    <div class="flex flex-row">
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://bit.ly/MK8DX-NITA-150"><LinkSolid class="mr-2" />Website</Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="http://discord.gg/9jc88HW">
            <DiscordSolid class="mr-2" />Discord </Button
          >
      </div>
    </div>
  </Section>
</main>
 
<!--
  <div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
    <a href="/{$page.params.lang}/time-trials/mk8dx" style="flex: 1 1 calc(33.333% - 10px); text-decoration: none;">
      <Button
        style="width: 100%; padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;"
      >
        <img src={MK8DX} alt="Mario Kart 8 Deluxe" style="max-width: 100%;" />
      </Button>
    </a>
    <a href="/{$page.params.lang}/time-trials/mk8" style="flex: 1 1 calc(33.333% - 10px); text-decoration: none;">
      <Button
        style="width: 100%; padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;"
      >
        <img src={MK8} alt="Mario Kart 8" style="max-width: 100%;" />
      </Button>
    </a>
    <a href="/{$page.params.lang}/time-trials/mk7" style="flex: 1 1 calc(33.333% - 10px); text-decoration: none;">
      <Button
        style="width: 100%; padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;"
      >
        <img src={MK7} alt="Mario Kart 7" style="max-width: 100%;" />
      </Button>
    </a>
    <a href="/{$page.params.lang}/time-trials/mkw" style="flex: 1 1 calc(33.333% - 10px); text-decoration: none;">
      <Button
        style="width: 100%; padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;"
      >
        <img src={MKW} alt="Mario Kart Wii" style="max-width: 100%;" />
      </Button>
    </a>
  </div>
-->

<style>
  main.container {
    max-width: 1200px;
    margin: 20px auto 20px auto;
  }
</style>
