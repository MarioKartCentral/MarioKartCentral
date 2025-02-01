<script lang="ts">
    import Badge from "./Badge.svelte";
    import LL from "$i18n/i18n-svelte";
</script>

<Badge badgeClass="captain_badge">{$LL.TOURNAMENTS.REGISTRATIONS.CAPTAIN()}</Badge>
