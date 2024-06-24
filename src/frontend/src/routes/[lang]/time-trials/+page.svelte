<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import LL from '$i18n/i18n-svelte';
  import MK8DX from '$lib/assets/logo_mk8dx.png';
  import MK8 from '$lib/assets/logo_mk8.png';
  import MK7 from '$lib/assets/logo_mk7.png';
  import MKW from '$lib/assets/logo_mkw.png';

</script>

<Section header={$LL.NAVBAR.TIME_TRIALS()}>
  <div slot="header_content">
  </div>
</Section>

<div>
  <p>
    This page is currently a work in progress, but it will eventually be the hub for everything 
    time trials. For now, players can find leaderboards on several other sites.
    This is the hub of Mario Kart Time Trials. Here, you'll find the most 
    up-to-date rankings for Mario Kart 8 Deluxe, Mario Kart 8, Mario Kart 7, and 
    Mario Kart Wii, with every category imagineable. Submit your times
    to see where you stack up!
  </p>
</div>

<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
  <Button style="flex: 1 1 calc(33.333% - 10px); paddinwg: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;">
    <img src={MK8DX} alt="Mario Kart 8 Deluxe" style="max-width: 100%;">
  </Button>
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;">
    <img src={MK8} alt="Mario Kart 8" style="max-width: 100%;">
  </Button>
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;">
    <img src={MK7} alt="Mario Kart 7" style="max-width: 100%;">
  </Button>
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent; display: flex; justify-content: center; align-items: center;">
    <img src={MKW} alt="Mario Kart Wii" style="max-width: 100%;">
  </Button>
</div>