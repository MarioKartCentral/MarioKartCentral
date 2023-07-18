<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';

    let id = 0;

    onMount(async () => {
        let param_id = $page.url.searchParams.get('id');
        id = Number(param_id);

    });
</script>