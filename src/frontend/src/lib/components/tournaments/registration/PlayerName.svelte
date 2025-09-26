<script lang="ts">
  import CaptainBadge from '$lib/components/badges/CaptainBadge.svelte';
  import { page } from '$app/stores';
  import RepresentativeBadge from '$lib/components/badges/RepresentativeBadge.svelte';
  import BaggerBadge from '$lib/components/badges/BaggerBadge.svelte';

  export let player_id: number;
  export let name: string;
  export let is_squad_captain: boolean = false;
  export let is_representative: boolean = false;
  export let is_bagger_clause: boolean = false;
</script>

<div class={is_squad_captain ? 'captain' : is_representative ? 'representative' : ''}>
  <a href="/{$page.params.lang}/registry/players/profile?id={player_id}">
    {name}
  </a>
  {#if is_squad_captain}
    <CaptainBadge />
  {:else if is_representative}
    <RepresentativeBadge />
  {/if}
  {#if is_bagger_clause}
    <BaggerBadge />
  {/if}
</div>

<style>
  a {
    margin-right: 5px;
  }
  .captain {
    color: #99e6ff;
    font-weight: 700;
  }
  .representative {
    color: #ffdd99;
    font-weight: 700;
  }
</style>
