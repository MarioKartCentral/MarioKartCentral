<script lang="ts">
    import { permissions, addPermission } from "$lib/util/util";
    import PermissionCheck from "$lib/components/common/PermissionCheck.svelte";
    import { page } from "$app/stores";
    import CreateEditTemplateForm from "$lib/components/tournaments/templates/CreateEditTemplateForm.svelte";
    
    addPermission(permissions.edit_tournament_template);

    let param_temp_id = $page.url.searchParams.get('template_id');
    let template_id = param_temp_id ? Number(param_temp_id) : null;
</script>

<PermissionCheck permission={permissions.edit_tournament_template}>
    {#if template_id}
        <CreateEditTemplateForm template_id={template_id} is_edit={true}/>
    {/if}
</PermissionCheck>