<script lang="ts">
    import { permissions, addPermission } from "$lib/util/util";
    import PermissionCheck from "$lib/components/common/PermissionCheck.svelte";
    import CreateEditTournamentSeriesForm from "$lib/components/tournaments/series/CreateEditTournamentSeriesForm.svelte";

    addPermission(permissions.create_series);
</script>

<PermissionCheck permission={permissions.create_series}>
    <CreateEditTournamentSeriesForm/>
</PermissionCheck>