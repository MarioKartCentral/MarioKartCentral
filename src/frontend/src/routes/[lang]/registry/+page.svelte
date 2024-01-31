<script lang="ts">
  import { page } from '$app/stores';
  import Section from '$lib/components/common/Section.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<Section header={$LL.MKC_REGISTRY()}>
  <p>
    <a href="/{$page.params.lang}/registry/players">{$LL.PLAYER_LIST.PLAYERS()}</a>
  </p>
  <p>
    <a href="/{$page.params.lang}/registry/teams">{$LL.TEAM_LIST.TEAMS()}</a>
  </p>
</Section>
