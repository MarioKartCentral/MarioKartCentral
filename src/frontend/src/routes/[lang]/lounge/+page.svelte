<script lang="ts">
  import Section from '$lib/components/common/Section.svelte';
  import Logo150Animated from '$lib/assets/logo_lounge150.gif';
  import Logo200 from '$lib/assets/logo_lounge200.png';
  import LogoMKW from '$lib/assets/logo_loungemkw.jpg';
  import LogoMKTC from '$lib/assets/logo_loungemktc.png';
  import LogoMK7 from '$lib/assets/logo_loungemk7.png';
  import LogoMKWorld from '$lib/assets/logo_loungemkworld.gif';
  import GameBadge from '$lib/components/badges/GameBadge.svelte';
  import DiscordInviteButton from '$lib/components/common/buttons/DiscordInviteButton.svelte';
  import LinkButton from '$lib/components/common/buttons/LinkButton.svelte';
  import LL from '$i18n/i18n-svelte';
</script>

<main class="container">
  <h1>{$LL.LOUNGE.LOUNGE()}</h1>

  <h2>{$LL.GAMES.MKWORLD()}</h2>
  <GameBadge game="mkworld" />
  <Section header={'Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={LogoMKWorld} alt="Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <LinkButton href="https://lounge.mkcentral.com/mkworld">{$LL.LOUNGE.WEBSITE()}</LinkButton>
        </div>
        <div class="mb-2 mx-2">
          <DiscordInviteButton href="https://discord.gg/WR6JKPn2v9"/>
        </div>
      </div>
    </div>
  </Section>

  <h2>{$LL.GAMES.MK8DX()}</h2>
  <GameBadge game="mk8dx" />
  <Section header={'150cc Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={Logo150Animated} alt="150cc Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <LinkButton href="https://lounge.mkcentral.com/mk8dx">{$LL.LOUNGE.WEBSITE()}</LinkButton>
        </div>
        <div class="mb-2 mx-2">
          <DiscordInviteButton href="https://discord.gg/revmGkE"/>
        </div>
      </div>
    </div>
  </Section>

  <Section header={'200cc Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={Logo200} alt="200cc Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <LinkButton href="https://200-lounge.com/">{$LL.LOUNGE.WEBSITE()}</LinkButton>
        </div>
        <div class="mb-2 mx-2">
          <DiscordInviteButton href="https://discord.gg/dfdRkFu"/>
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
          <LinkButton href="http://www.mariokarttour.net/">{$LL.LOUNGE.WEBSITE()}</LinkButton>
        </div>
        <div class="mb-2 mx-2">
          <DiscordInviteButton href="https://discord.gg/vYr3bQQHFY"/>
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
          <LinkButton href="https://mkwlounge.gg">{$LL.LOUNGE.WEBSITE()}</LinkButton>
        </div>
        <div class="mb-2 mx-2">
          <DiscordInviteButton href="https://discord.gg/mkw"/>
        </div>
      </div>
    </div>
  </Section>
  <h2>{$LL.GAMES.MK7()}</h2>
  <GameBadge game="mk7" />
  <Section header={'Lounge'}>
    <div class="flex flex-row">
      <img class="w-32 h-32" src={LogoMK7} alt="MK7 Lounge" />
      <div class="flex flex-col justify-start">
        <div class="mb-2 mx-2">
          <DiscordInviteButton href="https://discord.gg/cZZp9DdQ5e"/>
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
