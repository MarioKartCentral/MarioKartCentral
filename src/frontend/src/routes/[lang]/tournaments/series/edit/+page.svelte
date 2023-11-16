<script lang="ts">
    import { page } from "$app/stores";
    import { permissions, addPermission, setSeriesPerms, series_permissions } from "$lib/util/util";
    import SeriesPermissionCheck from "$lib/components/common/SeriesPermissionCheck.svelte";
    import CreateEditTournamentSeriesForm from "$lib/components/tournaments/series/CreateEditTournamentSeriesForm.svelte";

    setSeriesPerms();
    addPermission(permissions.edit_series);

    let param_id = $page.url.searchParams.get('id');
    let series_id = param_id ? Number(param_id) : null;
</script>

{#if series_id}
    <SeriesPermissionCheck series_id={series_id} permission={series_permissions.edit_series}>
        <CreateEditTournamentSeriesForm series_id={series_id} is_edit={true}/> 
    </SeriesPermissionCheck>
{/if}