<script lang="ts">
  import LL from '$i18n/i18n-svelte';
  import TagBadge from '$lib/components/badges/TagBadge.svelte';
  import Table from '$lib/components/common/Table.svelte';
  export let teams;
</script>

<Table>
  <col class="placement" />
  <col class="team_tag" />
  <col class="team_name" />
  <col class="gold" />
  <col class="silver" />
  <thead><tr><th></th><th></th><th></th><th>👑</th><th>🥈</th><th>🥉</th></tr></thead>
  <col class="bronze" />
  {#each teams as team}
    <tr>
      <td>{team.podiumsPlacement}</td>
      <td><TagBadge tag={team.squad.tag} color={1} /></td>
      <td>{team.squad.name}</td>
      <td>{team.gold}</td>
      <td>{team.silver}</td>
      <td>{team.bronze}</td>
    </tr>
  {/each}
</Table>

<style></style>
