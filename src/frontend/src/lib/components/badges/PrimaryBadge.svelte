<script lang="ts">
    import Badge from "./Badge.svelte";
</script>

<Badge badgeClass="primary">Primary</Badge>

<style>
    :global(.primary) {
        background-color: #029dbd;
        border: 1px solid #027d99;
  }
</style>