<script lang="ts">
    import Badge from "./Badge.svelte";
    import LL from "$i18n/i18n-svelte";
</script>

<Badge badgeClass='team_manager_badge'>{$LL.TEAM_PROFILE.MANAGER()}</Badge>