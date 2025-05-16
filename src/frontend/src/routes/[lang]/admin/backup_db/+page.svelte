<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { check_permission, permissions } from "$lib/util/permissions";
    import LL from "$i18n/i18n-svelte";

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    let working = false;
    async function backup_db() {
        working = true;
        const endpoint = '/api/admin/db_backup';
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        working = false;
        const result = await res.json();
        if(res.status === 200) {
            alert("Successfully backed up database!");
        }
        else {
            alert(`Failed to backup database: ${result['title']}`);
        }
    }
</script>

{#if user_info.is_checked}
    {#if check_permission(user_info, permissions.create_db_backups)}
        <Section header="Backup Database">
            <Button on:click={backup_db} {working}>Backup Database</Button>
        </Section>
    {:else}
        {$LL.COMMON.NO_PERMISSION()}
    {/if}
{/if}

