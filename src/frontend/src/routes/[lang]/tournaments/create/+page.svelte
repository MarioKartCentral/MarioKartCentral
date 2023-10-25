<script lang="ts">
    import { page } from "$app/stores";
    import CreateTournamentForm from "$lib/components/tournaments/create/CreateTournamentForm.svelte";
    
    let param_temp_id = $page.url.searchParams.get('template_id');
    let template_id = param_temp_id ? Number(param_temp_id) : null;
</script>

<CreateTournamentForm template_id={template_id}/>