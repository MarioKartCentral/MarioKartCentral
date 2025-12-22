<script lang="ts">
  import { DiscordSolid } from 'flowbite-svelte-icons';
  import type { Discord } from '$lib/types/discord';
  import { fly } from 'svelte/transition';

  export let discord: Discord;
  export let enableUserIdToggle: boolean = false;

  let toggled: boolean = false;
  function toggleId() {
    toggled = !toggled;
  }

  let tag: keyof HTMLElementTagNameMap = enableUserIdToggle ? 'button' : 'div';
  const elements = {
    button: {
      tag: 'button',
      onclick: toggleId,
      role: undefined,
    },
    div: {
      tag: 'div',
      onclick: null,
      role: undefined,
    },
  };
  const element = elements[tag];

  $: username = toggled ? discord.discord_id : discord.username;
</script>

<div class="flex">
  <svelte:element this={element.tag} on:click|preventDefault={element.onclick} role={element.role}>
    <DiscordSolid />
  </svelte:element>
  {#key toggled}
    <div class="username" in:fly={{ y: -20, duration: 250 }}>
      {username}
    </div>
  {/key}
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
