<script lang="ts">
  import Badge from './Badge.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<Badge badgeClass="team_leader_badge">{$LL.TEAMS.PROFILE.LEADER()}</Badge>
