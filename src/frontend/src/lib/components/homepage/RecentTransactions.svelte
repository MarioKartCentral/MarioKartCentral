<script lang="ts">
  import type { TeamTransfer, TransferList } from '$lib/types/team-transfer';
  import { onMount } from 'svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import { page } from '$app/stores';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import ArrowRight from '$lib/components/common/ArrowRight.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import BaggerBadge from '$lib/components/badges/BaggerBadge.svelte';
  import LL from '$i18n/i18n-svelte';
  import HomeSection from './HomeSection.svelte';

  export let style: string;
  let transfers: TeamTransfer[] = [];

  async function fetchData() {
    let url = `/api/registry/teams/transfers/approved`;
    const res = await fetch(url);
    if (res.status !== 200) {
      return;
    }
    const body: TransferList = await res.json();
    transfers = body.transfers.slice(0, 6);
  }

  onMount(fetchData);
</script>

<HomeSection
  header={$LL.HOMEPAGE.RECENT_TRANSACTIONS()}
  link="/{$page.params.lang}/registry/teams/transfers"
  linkText={$LL.HOMEPAGE.MORE_RECENT_TRANSACTIONS()}
  {style}
>
  {#if transfers.length}
    <div class="flex flex-col gap-[5px]">
      {#each transfers as transfer (transfer.invite_id)}
        <div class="row">
          <div class="flex items-center gap-[8px] mb-1">
            <div class="flag">
              <Flag country_code={transfer.player_country_code} />
            </div>
            <a href="/{$page.params.lang}/registry/players/profile?id={transfer.player_id}">
              {transfer.player_name}
            </a>
            {#if transfer.is_bagger_clause}
              <BaggerBadge />
            {/if}
          </div>
          <div class="flex items-center justify-between gap-4">
            <div class="left">
              <div class="badges flex flex-col sm:flex-row">
                <GameBadge game={transfer.game} />
                <ModeBadge mode={transfer.mode} />
              </div>
            </div>
            <div class="right">
              {#if transfer.roster_leave}
                <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_leave.team_id}">
                  <TagBadge tag={transfer.roster_leave.roster_tag} color={transfer.roster_leave.team_color} />
                </a>
              {:else}
                <i class="text-[9pt]">{$LL.TEAMS.TRANSFERS.NO_TEAM()}</i>
              {/if}
              <ArrowRight />
              {#if transfer.roster_join}
                <a href="/{$page.params.lang}/registry/teams/profile?id={transfer.roster_join.team_id}">
                  <TagBadge tag={transfer.roster_join.roster_tag} color={transfer.roster_join.team_color} />
                </a>
              {:else}
                {$LL.TEAMS.TRANSFERS.NO_TEAM()}
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</HomeSection>

<style>
  .row {
    background-color: rgba(255, 255, 255, 0.15);
    padding: 10px;
    font-size: 0.9rem;
  }
  .row:nth-child(odd) {
    background-color: rgba(210, 210, 210, 0.15);
  }
  .flag {
    zoom: 85%;
  }
  .right {
    display: flex;
    align-items: center;
    margin-top: auto;
    gap: 5px;
  }
  .badges {
    zoom: 80%;
  }
</style>
