<script lang="ts">
  import Badge from './Badge.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<Badge badgeClass="new_badge">{$LL.COMMON.NEW()}</Badge>
