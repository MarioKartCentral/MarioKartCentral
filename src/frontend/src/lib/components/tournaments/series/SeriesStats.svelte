<script lang="ts">
  import { onMount } from 'svelte';
  import LL from '$i18n/i18n-svelte';
  import Table from '$lib/components/common/Table.svelte';
  import { page } from '$app/stores';
  import type { Tournament } from '$lib/types/tournament';
  export let tournaments: Tournament[];
  let teams = [];

  function addTeams(tournaments) {
    for (let tournament of tournaments) {
      for (let team of placements) {
        
      }
    }
  }

  onMount(() => {
    if (tournaments) {
      teams = addTeams(tournaments);
      console.log(teams);
    }
  });
</script>

<div>{teams.length}</div>

<style></style>
