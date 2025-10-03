<script lang="ts">
  import type { Discord } from '$lib/types/discord';
  import DiscordName from './DiscordName.svelte';

  export let discord: Discord | null;

  let default_avatar = 'https://cdn.discordapp.com/embed/avatars/0.png?size=64';
  let discord_avatar_url = 'https://cdn.discordapp.com/avatars';

  $: avatar_url = discord?.avatar
    ? `${discord_avatar_url}/${discord.discord_id}/${discord.avatar}.png?size=64`
    : default_avatar;
</script>

{#if discord}
  <div class="flex">
    {#if avatar_url}
      <div class="section avatar">
        <img src={avatar_url} alt={discord.username} />
      </div>
    {/if}
    <div class="section">
      {#if discord.global_name}
        <div>
          {discord.global_name}
        </div>
      {/if}
      <DiscordName {discord} />
    </div>
  </div>
{/if}

<style>
  div.flex {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }
  div.section {
    margin: 5px 10px;
  }
  div.avatar {
    width: 64px;
  }
</style>
