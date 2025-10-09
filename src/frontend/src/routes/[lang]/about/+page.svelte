<script lang="ts">
  import LL from '$i18n/i18n-svelte';
</script>

<svelte:head>
  <title>About Us | MKCentral</title>
</svelte:head>

<div class="container mx-auto px-4 py-8 max-w-screen-lg text-gray-200">
  <h1 class="text-4xl font-bold mb-6 text-center text-white">About MKCentral</h1>

  <div class="mb-8">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    <p class="mb-6 text-lg">{@html $LL.HOMEPAGE.SUMMARY()}</p>
  </div>

  <div class="space-y-10">
    <section>
      <h2 class="text-2xl font-semibold mb-4 text-white">What We Offer</h2>

      <div class="mb-8">
        <h3 class="text-xl font-semibold mb-3 text-white">Player and Team Registry</h3>
        <p class="mb-4">
          MKCentral maintains a registry of players across the community, each with a dedicated profile page. Players
          can also create and join teams to participate in organized team tournaments. Each team has its own profile and
          match history.
        </p>
      </div>

      <div>
        <h3 class="text-xl font-semibold mb-3 text-white">Tournaments</h3>
        <p class="mb-4">
          We provide tools and infrastructure for community members to create and manage their own Mario Kart
          tournaments. Players and teams can easily discover, register, and participate in events through MKCentral.
          Player and team profiles display past tournaments and placements.
        </p>

        <div class="bg-gray-800 border-l-4 border-yellow-500 p-4 mb-4">
          <p class="font-medium">
            <strong>Disclaimer:</strong> MKCentral is not affiliated with or sponsored by Nintendo. All tournaments are
            independently organized by community members. MKCentral does not run or oversee events and is not
            responsible for ensuring compliance with
            <a
              href="https://en-americas-support.nintendo.com/app/answers/detail/a_id/63433/~/community-tournament-guidelines"
              class="text-blue-400 hover:text-blue-300">Nintendo's Community Tournament Guidelines</a
            >
            or Terms of Service.
          </p>
        </div>
      </div>
    </section>

    <section>
      <h2 class="text-2xl font-semibold mb-4 text-white">Community & Moderation</h2>
      <p class="mb-4">
        MKCentral is a completely free, nonprofit platform maintained by a team of passionate volunteers. Our site is <a
          href="https://github.com/MarioKartCentral/MarioKartCentral"
          class="text-blue-400 hover:text-blue-300">open-source</a
        >, and we welcome contributions from developers and community members on GitHub.
      </p>

      <p class="mb-4">
        We currently do not accept donations or display ads, though we may explore community-supported funding options
        in the future to sustain the platform.
      </p>

      <p class="mb-4">
        We operate several official Discord communities where players can socialize, ask for support, and get involved
        in the scene. Our moderation team works to ensure the community stays safe and welcoming. They handle reports,
        issue warnings, and take action when needed. If you have a concern or want to report a violation, please reach
        out via our Discord support channels.
      </p>
    </section>

    <section>
      <h2 class="text-2xl font-semibold mb-4 text-white">Copyright & Trademarks</h2>
      <p>
        Mario Kart and related trademarks are the property of Nintendo. MKCentral is an independent, fan-run community
        and is not endorsed by or affiliated with Nintendo in any way.
      </p>
    </section>
  </div>
</div>

<style lang="postcss">
  a:not([class]) {
    text-decoration: underline;
    color: #4dabf7;
  }
  a:not([class]):hover {
    color: #74c0fc;
  }
</style>
