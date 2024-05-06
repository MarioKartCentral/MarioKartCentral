<script lang="ts">
  import Badge from "./Badge.svelte";

  export let type: string;
  export let size: "mid" | "wide" = "mid";
</script>

<Badge badgeClass={'type_' + type.toLowerCase() + '_badge ' + size}>{type}</Badge>

<style>

  :global(.type_team_badge) {
    background-color: #006ea1;
    border: 1px solid #004c80;
  }

  :global(.type_solo_badge) {
    background-color: #a1006b;
    border: 1px solid #6b0040;
  }

  :global(.type_squad_badge) {
    background-color: #006633;
    border: 1px solid #005621;
  }
</style>
