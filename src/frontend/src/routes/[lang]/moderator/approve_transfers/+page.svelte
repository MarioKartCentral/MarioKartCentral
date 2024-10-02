<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import TransferList from '$lib/components/registry/teams/TransferList.svelte';
  import ForceTransferPlayer from '$lib/components/registry/teams/ForceTransferPlayer.svelte';
</script>

<Section header="Transfers">
  <TransferList approval_status="pending"/>
</Section>
<Section header="Manually Transfer Player">
  <ForceTransferPlayer/>
</Section>
