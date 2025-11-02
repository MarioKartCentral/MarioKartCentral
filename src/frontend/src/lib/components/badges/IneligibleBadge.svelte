<script lang="ts">
  import Badge from './Badge.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<Badge badgeClass="ineligible_badge">{$LL.TOURNAMENTS.REGISTRATIONS.INELIGIBLE()}</Badge>
