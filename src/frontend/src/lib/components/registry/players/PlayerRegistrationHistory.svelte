<script lang="ts">
  import { page } from '$app/stores';
  import { valid_team_modes } from '$lib/util/util';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { PlayerTransferItem } from '$lib/types/player-transfer';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';

  let game: string | null = null;
  let mode: string | null = null;
  // Default game + mode, because the component allows null
  game = 'mk8dx';
  mode = valid_team_modes[game][0];
  let history: PlayerTransferItem[] = [];
  let filtered_history: PlayerTransferItem[] = [];

  export let player: PlayerInfo;

  function toDate(unix_timestamp: number) {
    return new Date(unix_timestamp * 1000).toLocaleDateString();
  }

  async function fetchData() {
    // API
    let url = `/api/registry/players/${player.id}/getPlayerTransferHistory`;
    const res = await fetch(url);
    if (res.status !== 200) {
      return;
    }
    let body = await res.json();
    history = body.history;
    console.log(history);
    filterData();
  }

  async function filterData() {
    filtered_history = [...history];
    if (game) {
      filtered_history = filtered_history.filter((item) => item.game === game);
    }
    if (mode) {
      filtered_history = filtered_history.filter((item) => item.mode === mode);
    }
  }

  onMount(fetchData);
</script>

{#if history.length <= 0}
  <div></div>
{:else}
  <Section header={$LL.REGISTRATION_HISTORY.REGISTRATION_HISTORY()}>
    <div>
      <div>
        <form on:submit|preventDefault={filterData}>
          <div class="flex flex-row flex-wrap items-center justify-center">
            <GameModeSelect bind:game bind:mode hide_labels is_team />
            <div class="ml-1 my-2">
              <Button type="submit">Filter</Button>
            </div>
          </div>
        </form>
        <Table>
          <thead>
            <tr>
              <th>Team</th>
              <th>Registration Period</th>
            </tr>
          </thead>
          <tbody>
            {#each filtered_history as record, i}
              <tr class="row-{i % 2}">
                <td>
                  <a
                    class="hover:text-emerald-400"
                    href="/{$page.params.lang}/registry/teams/profile?id={record.team_id}"
                  >
                    <!-- prefer roster name, but use team name as fallback -->
                    {record.roster_name ? record.roster_name : record.team_name}
                  </a>
                </td>
                <td>
                  {toDate(record.join_date)} - {record.leave_date ? toDate(record.leave_date) : 'Present'}
                </td>
              </tr>
            {/each}
          </tbody>
        </Table>
      </div>
    </div>
  </Section>
{/if}
