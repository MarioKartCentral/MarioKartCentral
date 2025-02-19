<script lang="ts">
  import Badge from "./Badge.svelte";
  import LL from "$i18n/i18n-svelte";

  export let is_squad: boolean;
  export let teams_allowed: boolean;
  export let style = '';

  let type = is_squad ? (teams_allowed ? $LL.TOURNAMENTS.TYPES.TEAM() : $LL.TOURNAMENTS.TYPES.SQUAD()) : $LL.TOURNAMENTS.TYPES.SOLO();
</script>

<Badge badgeClass='type_{is_squad ? (teams_allowed ? 'team' : 'squad') : 'solo'}_badge wide' {style}>{type}</Badge>