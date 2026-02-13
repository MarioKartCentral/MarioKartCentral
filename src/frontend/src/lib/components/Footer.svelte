<script lang="ts">
  import { page } from '$app/stores';
  import { XSolid, YoutubeSolid, GithubSolid } from 'flowbite-svelte-icons';
  import Twitch from '$lib/components/icons/Twitch.svelte';
</script>

<div class="footer p-2">
  <div class="flex flex-col sm:flex-row gap-2">
    <ul class="flex flex-row gap-2 items-center">
      <li>
        <a href="https://www.youtube.com/c/MarioKartCentral" rel="external" title="YouTube" aria-label="YouTube">
          <YoutubeSolid size="lg" aria-hidden="true" />
        </a>
      </li>
      <li>
        <a href="https://twitter.com/mk_central" rel="external" title="Twitter" aria-label="X (formerly Twitter)">
          <XSolid size="lg" aria-hidden="true" />
        </a>
      </li>
      <li>
        <a href="https://www.twitch.tv/mariokartcentral" rel="external" title="Twitch" aria-label="Twitch">
          <Twitch size="md" />
        </a>
      </li>
      <li>
        <a
          href="https://github.com/MarioKartCentral/MarioKartCentral"
          rel="external"
          title="Github"
          aria-label="GitHub"
        >
          <GithubSolid size="lg" aria-hidden="true" />
        </a>
      </li>
    </ul>
    <ul class="flex flex-col gap-2 sm:text-end sm:flex-row sm:ml-auto sm:items-center">
      <li><a href="/{$page.params.lang}/about">About Us</a></li>
      <li><a href="/{$page.params.lang}/user/terms">Terms and Rules</a></li>
      <li><a href="/{$page.params.lang}/user/privacy-policy">Privacy Policy</a></li>
    </ul>
  </div>
  <div class="text-end text-gray-400">&copy; 2018-2026 mkcentral.com Mario Kart&trade; and &copy; Nintendo.</div>
</div>

<style>
  .footer {
    background-color: #313030;
    font-size: 14px;
  }

  a {
    text-decoration: none;
  }
</style>
