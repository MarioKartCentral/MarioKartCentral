<script lang="ts">
  import type { Team } from '$lib/types/team';
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import TransferList from './TransferList.svelte';
  import { sortFilterRosters } from '$lib/util/util';
  import LL from '$i18n/i18n-svelte';
  import { game_abbreviations } from '$lib/util/util';

  export let team: Team;
  let roster_id: number | null = null;

  let show = false;
</script>

<Section header={$LL.TEAMS.PROFILE.TRANSFER_HISTORY()}>
  <div slot="header_content">
    <Button on:click={() => (show = !show)}>
      {show ? $LL.COMMON.HIDE() : $LL.COMMON.SHOW()}
    </Button>
  </div>
  {#if show}
    <div class="roster-select">
      <select bind:value={roster_id}>
        <option value={null}>{$LL.TEAMS.PROFILE.ALL_ROSTERS()}</option>
        {#each sortFilterRosters(team.rosters) as roster}
          <option value={roster.id}>{roster.name} ({game_abbreviations[roster.game]})</option>
        {/each}
      </select>
    </div>

    {#key roster_id}
      <TransferList approval_status="approved" team_id={team.id} {roster_id} />
    {/key}
  {/if}
</Section>

<style>
  .roster-select {
    margin-bottom: 10px;
  }
</style>
