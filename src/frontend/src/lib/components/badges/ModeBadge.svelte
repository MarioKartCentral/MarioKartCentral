<script lang="ts">
  import Badge from "./Badge.svelte";
  import { mode_names } from "$lib/util/util";

  export let mode: string;
</script>

<Badge badgeClass={'mode_' + mode.toLowerCase() + '_badge wide'}>{mode_names[mode]}</Badge>