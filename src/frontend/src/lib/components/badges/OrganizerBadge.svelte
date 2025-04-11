<script lang="ts">
    import Badge from "./Badge.svelte";
    import LL from "$i18n/i18n-svelte";
    
    export let organizer: string;
    export let style = '';

</script>

{#if organizer === "Affiliate"}
    <Badge badgeClass="organizer_affiliate_badge wide" {style}>{$LL.TOURNAMENTS.MANAGE.ORGANIZED_BY_AFFILIATE()}</Badge>
{:else if organizer === "LAN"}
    <Badge badgeClass="organizer_lan_badge wide" {style}>{$LL.TOURNAMENTS.MANAGE.ORGANIZED_BY_LAN()}</Badge>
{/if}