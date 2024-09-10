<script lang="ts">
  import Badge from "./Badge.svelte";

  export let type: string;
</script>

<Badge badgeClass={'type_' + type.toLowerCase() + '_badge wide'}>{type}</Badge>