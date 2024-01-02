<script lang="ts">
  import type { Tournament } from '$lib/types/tournament';

  export let tournament: Tournament;
  export let squad_color: number | null = null;
  export let squad_name: string | null = null;
  export let squad_tag: string | null = null;
</script>

{#if tournament.is_squad}
  <div>
    <label for="squad_color">Squad Color</label>
    <input type="number" min="1" name="squad_color" value={squad_color} required />
  </div>
{/if}
{#if tournament.squad_name_required}
  <div>
    <label for="squad_name">Squad Name</label>
    <input name="squad_name" value={squad_name} required />
  </div>
{/if}
{#if tournament.squad_tag_required}
  <div>
    <label for="squad_tag">Squad Tag</label>
    <input name="squad_tag" maxlength={tournament.game === 'mkt' ? 12 : 10} value={squad_tag} required />
  </div>
{/if}
