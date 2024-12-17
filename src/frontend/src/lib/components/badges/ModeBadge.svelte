<script lang="ts">
  import Badge from "./Badge.svelte";
  import LL from "$i18n/i18n-svelte";

  export let mode: string;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mode_strings: any = $LL.MODES;
</script>

<Badge badgeClass={'mode_' + mode.toLowerCase() + '_badge wide'}>{mode_strings[mode.toUpperCase()]()}</Badge>