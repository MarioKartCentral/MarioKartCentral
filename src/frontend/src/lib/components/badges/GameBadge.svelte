<script lang="ts">
  import Badge from './Badge.svelte';

  export let game: string;
</script>

<Badge badgeClass={'game_' + game + '_badge wide'}>{game.toUpperCase()}</Badge>