<script lang="ts">
  import { DiscordSolid } from 'flowbite-svelte-icons';
  import type { Discord } from '$lib/types/discord';

  export let discord: Discord;
</script>

<div class="flex">
  <DiscordSolid />
  <div class="username">
    {discord.username}
  </div>
</div>

<style>
  div.flex {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }
  div.username {
    margin-left: 5px;
  }
</style>
