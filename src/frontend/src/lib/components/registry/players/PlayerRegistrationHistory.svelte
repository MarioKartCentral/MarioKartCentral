<script lang="ts">
  import { page } from '$app/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { PlayerTransferItem } from '$lib/types/player-transfer';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/table/Table.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import GameModeSelect from '$lib/components/common/GameModeSelect.svelte';
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  import BaggerBadge from '$lib/components/badges/BaggerBadge.svelte';
  import { user } from '$lib/stores/stores';
  import { check_permission, permissions } from '$lib/util/permissions';

  let game: string | null = null;
  let mode: string | null = null;
  let show_hidden = false;
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
    if (!show_hidden || !check_permission($user, permissions.edit_player)) {
      filtered_history = filtered_history.filter((item) => !item.is_hidden);
    }
  }

  async function toggleTransferItemVisibility(record: PlayerTransferItem) {
    let conf = window.confirm($LL.PLAYERS.PROFILE.TOGGLE_TEAM_REGISTRATION_VISIBILITY_CONFIRM());
    if (!conf) return;
    const endpoint = `/api/registry/players/${player.id}/toggleTransferItemVisibility/${record.id}`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const result = await response.json();
    if (response.status < 300) {
      window.location.reload();
    } else {
      alert(`${$LL.PLAYERS.PROFILE.TOGGLE_TEAM_REGISTRATION_VISIBILITY_FAILED()}: ${result['title']}`);
    }
  }

  onMount(fetchData);
</script>

{#if history.length <= 0}
  <div></div>
{:else}
  <Section header={$LL.PLAYERS.REGISTRATION_HISTORY()}>
    <div>
      <div>
        <form on:submit|preventDefault={filterData}>
          <div class="flex gap-2 flex-row flex-wrap items-center justify-center">
            <GameModeSelect bind:game bind:mode hide_labels is_team all_option />
            {#if check_permission($user, permissions.edit_player)}
              <div class="ml-1 my-2">
                <select bind:value={show_hidden}>
                  <option value={false}>{$LL.PLAYERS.PROFILE.HIDE_HIDDEN_TEAM_REGISTRATIONS()}</option>
                  <option value={true}>{$LL.PLAYERS.PROFILE.SHOW_HIDDEN_TEAM_REGISTRATIONS()}</option>
                </select>
              </div>
            {/if}
            <div class="ml-1 my-2">
              <Button type="submit">{$LL.COMMON.FILTER()}</Button>
            </div>
          </div>
        </form>
        <Table data={filtered_history} let:item={record}>
          <tr slot="header">
            <th>Team</th>
            <th>Registration Period</th>
            <th />
          </tr>

          <tr class="row {record.is_hidden ? 'hidden-item' : ''}">
            <td>
              <a href="/{$page.params.lang}/registry/teams/profile?id={record.team_id}">
                <!-- prefer roster name, but use team name as fallback -->
                {record.roster_name ? record.roster_name : record.team_name}
                {#if record.is_bagger_clause}
                  <BaggerBadge />
                {/if}
              </a>
            </td>
            <td>
              {toDate(record.join_date)} - {record.leave_date ? toDate(record.leave_date) : 'Present'}
            </td>
            <td>
              {#if check_permission($user, permissions.edit_player)}
                <button class="link-button" on:click={() => toggleTransferItemVisibility(record)}>
                  {#if !record.is_hidden}
                    {$LL.COMMON.HIDE()}
                  {:else}
                    {$LL.COMMON.SHOW()}
                  {/if}
                </button>
              {/if}
            </td>
          </tr>
        </Table>
      </div>
    </div>
  </Section>
{/if}

<style>
  .hidden-item {
    opacity: 0.7;
  }
  button.link-button {
    background-color: transparent;
    border: none;
    color: white;
    cursor: pointer;
  }
</style>
