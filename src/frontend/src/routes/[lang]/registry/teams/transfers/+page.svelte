<script lang="ts">
    import Section from "$lib/components/common/Section.svelte";
    import TransferList from "$lib/components/registry/teams/TransferList.svelte";
</script>

<Section header="Transfers">
    <TransferList approval_status="approved"/>
</Section>