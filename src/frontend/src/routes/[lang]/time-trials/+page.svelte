<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import { DiscordSolid, LinkSolid } from 'flowbite-svelte-icons';
</script>

<div class="tt-container">
  <div class="disclaimer">
    This page is currently a work in progress. For now,
    players can find leaderboards on several other sites.
  </div>
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
</div>

<style>
  .tt-container {
    max-width: 1200px;
    margin: 20px auto 20px auto;
  }
  .disclaimer {
    margin-bottom: 20px;
  }
</style>
