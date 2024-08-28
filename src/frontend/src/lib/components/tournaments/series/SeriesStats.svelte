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
      <td>{team.podiums_placement}</td>
      <td><TagBadge tag={team.tag} color={1} /></td>
      <td>{team.name}</td>
      <td>{team.gold_medals}</td>
      <td>{team.silver_medals}</td>
      <td>{team.bronze_medals}</td>
    </tr>
  {/each}
</Table>

<style></style>
