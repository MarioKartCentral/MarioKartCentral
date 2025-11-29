<script lang="ts">
  import type { Discord } from '$lib/types/discord';
  import DiscordName from './DiscordName.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import { CalendarMonthSolid } from 'flowbite-svelte-icons';
  export let discord: Discord | null;
  export let displayJoinDate: boolean = false;

  let default_avatar = 'https://cdn.discordapp.com/embed/avatars/0.png?size=64';
  let discord_avatar_url = 'https://cdn.discordapp.com/avatars';

  $: avatar_url = discord?.avatar
    ? `${discord_avatar_url}/${discord.discord_id}/${discord.avatar}.png?size=64`
    : default_avatar;

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
  };

  function snowflakeToTimestamp(snowflake: string): number {
    const int = BigInt(snowflake) >> 22n;
    return Number(int) + 1420070400000;
  }
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
      {#if displayJoinDate}
        <div class="flex">
          <CalendarMonthSolid />
          {new Date(snowflakeToTimestamp(discord.discord_id)).toLocaleString($locale, options)}
        </div>
      {/if}
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
