<script lang="ts">
  import { colors } from '$lib/util/util';
  import Badge from './Badge.svelte';

  export let tag: string | null;
  export let color: number | null = null;

  $: color_val = colors[(color === null ? 0 : color) % colors.length].value;
</script>

<Badge badgeClass="tag_badge" style="background-color:{color_val};border: 1px solid {color_val}">
  {tag ? tag : "-"}
</Badge>
