<script lang="ts">
    import TemplateList from "$lib/components/tournaments/templates/TemplateList.svelte";
    import { page } from "$app/stores";

    let param_id = $page.url.searchParams.get('id');
    let id = Number(param_id);
</script>

<TemplateList series_id={id}/>