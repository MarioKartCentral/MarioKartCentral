<script lang="ts">
    import Badge from "./Badge.svelte";
</script>

<Badge badgeClass="captain_badge">Captain</Badge>

<style>
:global(.captain_badge) {
    width: 60px;
    font-weight: 700;
    background-color: #029dbd;
    border: 1px solid #027d99;
  }
</style>
