<script lang="ts">
  import { onMount } from 'svelte';
  import Section from '$lib/components/common/Section.svelte';
  import { addPermission, permissions } from '$lib/util/util';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
</script>

<Section header={$LL.NAVBAR.TIME_TRIALS()}>
  <div slot="header_content">
  </div>
</Section>

<div>
  <p>
    MKRecords is the hub for Mario Kart Time Trials. Here, you'll find the most 
    up-to-date rankings for Mario Kart 8 Deluxe, Mario Kart 8, Mario Kart 7, and 
    Mario Kart Wii, with every category imagineable. Submit your times
    to see where you stack up!
  </p>
</div>

<div style="display: flex; flex-wrap: wrap; gap: 10px;">
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent;">
    <img src="$lib/assets/logo_mk8dx.png" alt="Mario Kart 8 Deluxe" style="max-width: 100%;">
  </Button>
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent;">
    <img src="$lib/assets/logo_mk8.png" alt="Mario Kart 8" style="max-width: 100%;">
  </Button>
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent;">
    <img src="$lib/assets/logo_mk7.png" alt="Mario Kart 7" style="max-width: 100%;">
  </Button>
  <Button style="flex: 1 1 calc(33.333% - 10px); padding: 10px; border: none; background-color: transparent;">
    <img src="$lib/assets/logo_mkw.png" alt="Mario Kart Wii" style="max-width: 100%;">
  </Button>
</div>