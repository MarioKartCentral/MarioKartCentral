<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';
  import ColorSelect from '$lib/components/common/ColorSelect.svelte';
  import LL from '$i18n/i18n-svelte';
  import Input from '$lib/components/common/Input.svelte';

  export let tournament: Tournament;
  export let squad_color: number | null = null;
  export let squad_name: string | null = null;
  export let squad_tag: string | null = null;

  let entered_tag = squad_tag;
</script>

{#if tournament.is_squad}
  <div class="item">
    <span class="item-label">
      <label for="squad_color">{$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_COLOR_SELECT()}</label>
    </span>
    <ColorSelect name="squad_color" color={Number(squad_color)} tag={entered_tag}/>
  </div>
{/if}
{#if tournament.squad_name_required}
  <div class="item">
    <span class="item-label">
      <label for="squad_name">{$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_NAME()}</label>
    </span>
    <Input name="squad_name" value={squad_name} required no_white_space maxlength={32}/>
  </div>
{/if}
{#if tournament.squad_tag_required}
  <div class="item">
    <span class="item-label">
      <label for="squad_tag">{$LL.TOURNAMENTS.REGISTRATIONS.SQUAD_TAG()}</label>
    </span>
    <Input name="squad_tag" maxlength={8} bind:value={entered_tag} required no_white_space/>
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