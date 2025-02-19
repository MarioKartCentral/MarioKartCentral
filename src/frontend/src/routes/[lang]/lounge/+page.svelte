<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Button from '$lib/components/common/buttons/Button.svelte';
  import Logo150Animated from '$lib/assets/logo_lounge150.gif';
  import Logo200 from '$lib/assets/logo_lounge200.png';
  import LogoMKW from '$lib/assets/logo_loungemkw.jpg';
  import LogoMKTC from '$lib/assets/logo_loungemktc.png';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import { DiscordSolid, LinkSolid } from 'flowbite-svelte-icons';
  import LL from '$i18n/i18n-svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<main class="container">
  <h1>{$LL.LOUNGE.LOUNGE()}</h1>
  <h2>{$LL.GAMES.MK8DX()}</h2>
  <GameBadge game="mk8dx" />
  <Section header={'150cc Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={Logo150Animated} alt="150cc Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://mk8dx-lounge.com/"><LinkSolid class="mr-2" />{$LL.LOUNGE.WEBSITE()}</Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/revmGkE">
            <DiscordSolid class="mr-2" />{$LL.LOUNGE.DISCORD_INVITE()}</Button
          >
        </div>
      </div>
    </div>
  </Section>

  <Section header={'200cc Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={Logo200} alt="200cc Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://200-lounge.com/"><LinkSolid class="mr-2" />{$LL.LOUNGE.WEBSITE()}</Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/dfdRkFu">
            <DiscordSolid class="mr-2" />{$LL.LOUNGE.DISCORD_INVITE()}</Button
          >
        </div>
      </div>
    </div>
  </Section>

  <h2>{$LL.GAMES.MKT()}</h2>
  <GameBadge game="mkt" />
  <Section header={'Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={LogoMKTC} alt="MKTC Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="http://www.mariokarttour.net/"><LinkSolid class="mr-2" />{$LL.LOUNGE.WEBSITE()}</Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/vYr3bQQHFY">
            <DiscordSolid class="mr-2" />{$LL.LOUNGE.DISCORD_INVITE()}</Button
          >
        </div>
      </div>
    </div>
  </Section>

  <h2>{$LL.GAMES.MKW()}</h2>
  <GameBadge game="mkw" />
  <Section header={'Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={LogoMKW} alt="MKW Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <Button size="lg" href="https://mkwlounge.gg"><LinkSolid class="mr-2" />{$LL.LOUNGE.WEBSITE()}</Button>
        </div>
        <div class="mb-2 mx-2">
          <Button size="lg" color="blue" href="https://discord.gg/mkw">
            <DiscordSolid class="mr-2" />{$LL.LOUNGE.DISCORD_INVITE()}</Button
          >
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
