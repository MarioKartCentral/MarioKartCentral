<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import Button from "$lib/components/common/buttons/Button.svelte";

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

<Section header="Backup Database">
    <Button on:click={backup_db} {working}>Backup Database</Button>
</Section>