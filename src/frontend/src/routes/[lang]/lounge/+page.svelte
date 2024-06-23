<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Logo200 from '$lib/assets/logo_200lounge.png';
  import Logo150 from '$lib/assets/logo_150lounge.png';
  import LogoMKW from '$lib/assets/logo_mkwlounge.png';
  import LogoMKTC from '$lib/assets/logo_mktclounge.png';
  import ModeBadge from '$lib/components/badges/ModeBadge.svelte';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import { ArrowRightOutline, EnvelopeOutline } from 'flowbite-svelte-icons';
</script>

<main class="container">
  <h1>Lounge</h1>
  <h2>Mario Kart 8 Deluxe</h2>
  <GameBadge game="mk8" />
  <Section header={'MK8DX 150cc Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={Logo150} alt="150cc Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://mk8dx-lounge.com/">Website<ArrowRightOutline class="ml-2" /></Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/revmGkE">Discord Invite</Button>
        </div>
      </div>
    </div>
  </Section>

  <Section header={'MK8DX 200cc Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={Logo200} alt="200cc Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://200-lounge.com/">Website<ArrowRightOutline class="ml-2" /></Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/dfdRkFu">Discord Invite</Button>
        </div>
      </div>
    </div>
  </Section>

  <h2>Mario Kart Tour</h2>
  <GameBadge game="mkt" />
  <Section header={'MKTC Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={LogoMKTC} alt="MKTC Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/vYr3bQQHFY">Discord Invite</Button>
        </div>
      </div>
    </div>
  </Section>

  <h2>Mario Kart Wii</h2>
  <GameBadge game="mkw" />
  <Section header={'MKW Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={LogoMKW} alt="MKW Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/revmGkE">Discord Invite</Button>
        </div>
      </div>
    </div>
  </Section>
</main>

<style>
  main.container {
    max-width: 1200px;
    margin: 20px auto 20px auto;
  }
  h1 {
    font-size: 4rem;
    font-weight: 600;
  }
  h2 {
    font-size: 2rem;
    font-weight: 600;
  }
</style>
