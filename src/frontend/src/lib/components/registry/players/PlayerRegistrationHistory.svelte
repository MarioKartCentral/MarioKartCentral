<script lang="ts">
  import { page } from '$app/stores';
  import { user } from '$lib/stores/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import type { UserInfo } from '$lib/types/user-info';
  import type { PlayerTransferItem } from '$lib/types/player-transfer';
  import Section from '$lib/components/common/Section.svelte';
  import Table from '$lib/components/common/Table.svelte';
  import LL from '$i18n/i18n-svelte';
  import { onMount } from 'svelte';
  let history: PlayerTransferItem[] = [];
  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });
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
    console.log(body);
    history = body.history;
    console.log(history);
  }

  onMount(fetchData);
</script>

<Section header={$LL.PLAYER_REGISTRATION_HISTORY.REGISTRATION_HISTORY()}>
  <!-- Team history -->
  <div>
    <div>
      <Table>
        <thead>
          <tr>
            <th>Team</th>
            <th>Registration Period</th>
          </tr>
        </thead>
        <tbody>
          {#each history as record, i}
            <tr class="row-{i % 2}">
              <td>
                <a
                  class="hover:text-emerald-400"
                  href="/{$page.params.lang}/registry/teams/profile?id={record.team_id}"
                >
                  {record.roster_name ? record.roster_name : record.team_name}
                </a>
              </td>
              <td>
                {toDate(record.join_date)}
              </td>
            </tr>
          {/each}
        </tbody>
      </Table>
    </div>
  </div></Section
>
