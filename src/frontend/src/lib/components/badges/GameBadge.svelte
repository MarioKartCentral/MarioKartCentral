<script lang="ts">
  import Badge from './Badge.svelte';

  export let game: string;
  export let style = '';
</script>

<Badge badgeClass='game_{game}_badge wide' {style}>{game.toUpperCase()}</Badge>