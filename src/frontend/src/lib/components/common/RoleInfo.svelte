<script lang="ts">
  import type { Role } from '$lib/types/role';
  import type { RoleInfo } from '$lib/types/role';
  import { onMount } from 'svelte';
  import Table from './table/Table.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import { page } from '$app/stores';
  import type { PlayerInfo } from '$lib/types/player-info';
  import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import CancelButton from '$lib/components/common/buttons/CancelButton.svelte';
  import type { Player } from '$lib/types/player';
  import { locale } from '$i18n/i18n-svelte';
  import LL from '$i18n/i18n-svelte';

  export let role: Role;
  export let url: string;
  export let user_position: number;

  let role_info: RoleInfo;

  let selected_player: PlayerInfo | null = null;
  let expires_on: string | null = null;

  function is_expirable_role() {
    const expirable_roles = ['Banned', 'Host Banned'];
    return expirable_roles.includes(role.name);
  }

  onMount(async () => {
    await loadInfo();
  });

  async function loadInfo() {
    const res = await fetch(`${url}/roles/${role.id}`);
    if (res.status === 200) {
      const body: RoleInfo = await res.json();
      selected_player = null;
      role_info = body;
    }
  }

  async function giveRoleToPlayer(player_id: number) {
    let expires_on_payload: number | null = null;
    if (expires_on) {
      let date = new Date(expires_on);
      expires_on_payload = date.getTime() / 1000;
    }
    const payload = {
      player_id: player_id,
      role_name: role.name,
      expires_on: expires_on_payload,
    };
    const endpoint = `${url}/roles/grant`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      await loadInfo();
    } else {
      alert(`${$LL.ROLES.ADD_ROLE_FAILED()}: ${result['title']}`);
    }
  }

  async function removeRoleFromPlayer(player: Player) {
    let conf = window.confirm($LL.ROLES.REMOVE_ROLE_CONFIRM({ player_name: player.name, role_name: role.name }));
    if (!conf) return;
    const payload = {
      player_id: player.id,
      role_name: role.name,
    };
    const endpoint = `${url}/roles/remove`;
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (response.status < 300) {
      await loadInfo();
    } else {
      alert(`${$LL.ROLES.REMOVE_ROLE_FAILED()}: ${result['title']}`);
    }
  }

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };
</script>

<div>
  {#if role_info}
    <div class="role">
      {#if user_position < role.position}
        <div>
          {$LL.ROLES.ADD_PLAYER()}
        </div>
        <div class="addplayer">
          <PlayerSearch bind:player={selected_player} has_connected_user />
          {#if selected_player !== null}
            {#if is_expirable_role()}
              <label for="expires_on">{$LL.ROLES.UNTIL()}</label>
              <input name="expires_on" type="datetime-local" bind:value={expires_on} />
            {/if}
            <Button on:click={() => giveRoleToPlayer(Number(selected_player?.id))}>{$LL.ROLES.ADD_ROLE()}</Button>
          {/if}
        </div>
      {:else}
        <div>
          {$LL.ROLES.NO_EDIT_PERMISSION()}
        </div>
      {/if}
      <div class="table">
        <Table data={role_info.players} let:item={player}>
          <colgroup slot="colgroup">
            <col class="country" />
            <col class="name" />
            {#if is_expirable_role()}
              <col class="until mobile-hide" />
            {/if}
            <col class="remove" />
          </colgroup>
          <tr class="row">
            <td>
              <Flag country_code={player.country_code} />
            </td>
            <td>
              <a href="/{$page.params.lang}/registry/players/profile?id={player.id}">
                {player.name}
              </a>
            </td>
            {#if is_expirable_role()}
              <td class="mobile-hide">
                {#if player.expires_on}
                  {$LL.ROLES.ROLE_EXPIRES_ON({
                    date: new Date(player.expires_on * 1000).toLocaleString($locale, options),
                  })}
                {/if}
              </td>
            {/if}
            <td style="text-align:right;">
              {#if user_position < role.position}
                <div class="close">
                  <CancelButton on:click={() => removeRoleFromPlayer(player)} />
                </div>
              {/if}
            </td>
          </tr>
        </Table>
      </div>
    </div>
  {/if}
</div>

<style>
  div.role {
    display: flex;
    margin-top: 10px;
    text-align: center;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }
  div.addplayer {
    min-width: 350px;
    display: flex;
    gap: 10px;
  }
  div.table {
    display: table;
    margin: auto;
    min-width: 50%;
  }
  col.country {
    width: 15%;
  }
  col.name {
    width: 35%;
  }
  col.until {
    width: 20%;
  }
  col.remove {
    width: 30%;
  }
  .close {
    display: flex;
    flex-direction: row-reverse;
    padding-right: 10px;
  }
  label {
    display: flex;
    align-items: center;
  }
</style>
