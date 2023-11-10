<script lang="ts">
    import { permissions, addPermission } from "$lib/util/util";
    import PermissionCheck from "$lib/components/common/PermissionCheck.svelte";
    import CreateTournamentSeriesForm from "$lib/components/tournaments/series/create/CreateTournamentSeriesForm.svelte";

    addPermission(permissions.create_series);
</script>

<PermissionCheck permission={permissions.create_series}>
    <CreateTournamentSeriesForm/>
</PermissionCheck>