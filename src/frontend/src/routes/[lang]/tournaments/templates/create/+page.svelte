<script lang="ts">
    import CreateTemplateForm from "$lib/components/tournaments/templates/CreateTemplateForm.svelte";
    import { permissions, addPermission } from "$lib/util/util";
    import PermissionCheck from "$lib/components/common/PermissionCheck.svelte";
    
    addPermission(permissions.create_tournament_template);
</script>

<PermissionCheck permission={permissions.create_tournament_template}>
    <CreateTemplateForm/>
</PermissionCheck>