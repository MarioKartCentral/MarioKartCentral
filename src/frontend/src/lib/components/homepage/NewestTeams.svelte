<script lang="ts">
  import type { Team, TeamList } from '$lib/types/team';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import TagBadge from '../badges/TagBadge.svelte';
  import { onMount } from 'svelte';
  import HomeSection from './HomeSection.svelte';

  export let style: string;
  let latestTeams: Team[] = [];

  async function fetchLatestTeams() {
    const res = await fetch(`/api/registry/teams?is_historical=false&is_active=true&sort_by_newest=true`);
    if (res.status === 200) {
      const body: TeamList = await res.json();
      latestTeams = body.teams.slice(0, 10);
    }
  }

  onMount(fetchLatestTeams);
</script>

<HomeSection
  header={$LL.HOMEPAGE.NEWEST_TEAMS()}
  link="/{$page.params.lang}/registry/teams"
  linkText={$LL.HOMEPAGE.VIEW_ALL_TEAMS()}
  {style}
>
  {#if latestTeams.length}
    <div class="flex flex-col gap-[5px]">
      {#each latestTeams as team}
        <div class="row">
          <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">
            <TagBadge tag={team.tag} color={team.color} />
          </a>
          <a href="/{$page.params.lang}/registry/teams/profile?id={team.id}">{team.name}</a>
        </div>
      {/each}
    </div>
  {/if}
</HomeSection>

<style>
  .row {
    display: flex;
    font-size: 0.9rem;
    background-color: rgba(255, 255, 255, 0.15);
    padding: 0px 10px;
    height: 45px;
    align-items: center;
    gap: 10px;
  }
  .row:nth-child(odd) {
    background-color: rgba(210, 210, 210, 0.15);
  }
</style>
