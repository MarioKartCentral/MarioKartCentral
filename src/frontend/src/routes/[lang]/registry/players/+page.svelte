<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import PlayerList from '$lib/components/registry/players/PlayerList.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<Section header={$LL.PLAYER_LIST.PLAYER_LISTING()}>
  <PlayerList/>
</Section>