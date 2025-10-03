<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import type { Team } from '$lib/types/team';
  import TeamSearch from '$lib/components/common/TeamSearch.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, permissions } from '$lib/util/permissions';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let from_team: Team | null = null;
  let to_team: Team | null = null;

  async function mergeTeams() {
    if (!from_team || !to_team) {
      return;
    }
    if (from_team.id == to_team.id) {
      alert($LL.MODERATOR.SELECT_UNIQUE_TEAMS());
      return;
    }
    let conf = window.confirm($LL.MODERATOR.MERGE_TEAMS_CONFIRM({ old_team: from_team.name, new_team: to_team.name }));
    if (!conf) return;
    const payload = {
      from_team_id: from_team.id,
      to_team_id: to_team.id,
    };
    const endpoint = '/api/registry/teams/merge';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await res.json();
    if (res.status < 300) {
      alert($LL.MODERATOR.MERGE_TEAMS_SUCCESS());
      window.location.reload();
    } else {
      alert(`${$LL.MODERATOR.MERGE_TEAMS_FAILED()}: ${result['title']}`);
    }
  }
</script>

{#if user_info.is_checked}
  {#if check_permission(user_info, permissions.merge_teams)}
    <Section header={$LL.MODERATOR.MERGE_TEAMS()}>
      <div class="option">
        <div>
          {$LL.MODERATOR.OLD_TEAM()}:
        </div>
        <TeamSearch bind:team={from_team} />
      </div>

      {#if from_team}
        <div class="option">
          <div>{$LL.MODERATOR.NEW_TEAM()}:</div>
          <TeamSearch bind:team={to_team} />
        </div>
      {/if}
      {#if to_team}
        <Button on:click={mergeTeams}>{$LL.MODERATOR.MERGE_TEAMS()}</Button>
      {/if}
    </Section>
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}

<style>
  div.option {
    margin-bottom: 10px;
  }
</style>
