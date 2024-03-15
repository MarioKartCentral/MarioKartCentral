<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import ColorSelect from '$lib/components/common/ColorSelect.svelte';

  export let tournament: Tournament;
  export let squad_color: number | null = null;
  export let squad_name: string | null = null;
  export let squad_tag: string | null = null;

  let entered_tag = squad_tag;
</script>

{#if tournament.is_squad}
  <div class="item">
    <span class="item-label">
      <label for="squad_color">Squad Color</label>
    </span>
    <ColorSelect name="squad_color" color={Number(squad_color)} tag={entered_tag}/>
  </div>
{/if}
{#if tournament.squad_name_required}
  <div class="item">
    <span class="item-label">
      <label for="squad_name">Squad Name</label>
    </span>
    
    <input name="squad_name" value={squad_name} required />
  </div>
{/if}
{#if tournament.squad_tag_required}
  <div class="item">
    <span class="item-label">
      <label for="squad_tag">Squad Tag</label>
    </span>
    <input name="squad_tag" maxlength=5 bind:value={entered_tag} required />
  </div>
{/if}

<style>
  .item-label {
    display: inline-block;
    width: 150px;
    font-weight: 525;
  }
  .item {
    margin: 10px 0;
  }
</style>