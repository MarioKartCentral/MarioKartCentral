<script lang="ts">
    import { page } from "$app/stores";
    import CreateTournamentForm from "$lib/components/tournaments/create/CreateTournamentForm.svelte";
    import { permissions, addPermission } from "$lib/util/util";
    import PermissionCheck from "$lib/components/common/PermissionCheck.svelte";
    
    addPermission(permissions.create_tournament)

    let param_temp_id = $page.url.searchParams.get('template_id');
    let template_id = param_temp_id ? Number(param_temp_id) : null;
</script>

<PermissionCheck permission={permissions.create_tournament}>
    <CreateTournamentForm template_id={template_id}/>
</PermissionCheck>
