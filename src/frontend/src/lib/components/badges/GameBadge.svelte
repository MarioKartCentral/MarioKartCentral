<script lang="ts">
  import Badge from './Badge.svelte';
  import { game_abbreviations } from '$lib/util/util';

  export let game: string;
  export let style = '';
</script>

<Badge badgeClass='game_{game}_badge wide' {style}>{game_abbreviations[game]}</Badge>