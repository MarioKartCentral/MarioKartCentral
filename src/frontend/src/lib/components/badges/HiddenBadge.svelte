<script lang="ts">
  import Badge from './Badge.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<Badge badgeClass="hidden_badge">{$LL.POSTS.HIDDEN()}</Badge>
