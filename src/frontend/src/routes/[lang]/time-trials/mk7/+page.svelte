<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import MK7 from '$lib/assets/logo_mk7.png';

</script>

<Section header={$LL.NAVBAR.TIME_TRIALS()}>
  <div slot="header_content">
  </div>
</Section>

<div>
  <p>
    This is the home page for Mario Kart 7 time trials.
  </p>
</div>

<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;">
    <img src={MK7} alt="Mario Kart 7" style="max-width: 100%;">
  </Button>
</div>