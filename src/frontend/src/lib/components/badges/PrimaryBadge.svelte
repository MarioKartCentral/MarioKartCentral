<script lang="ts">
  import Badge from './Badge.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<Badge badgeClass="primary">{$LL.TOURNAMENTS.REGISTRATIONS.PRIMARY()}</Badge>
