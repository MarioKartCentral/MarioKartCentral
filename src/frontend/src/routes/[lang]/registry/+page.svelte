<script lang="ts">
  import { page } from '$app/stores';
  import Section from '$lib/components/common/Section.svelte';
</script>

<Section header="MKCentral Registry">
  <p>Players</p>
  <p>
    <a href="/{$page.params.lang}/registry/teams">Teams</a>
  </p>
</Section>
