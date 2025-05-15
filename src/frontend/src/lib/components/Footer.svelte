<script lang="ts">
  import { page } from "$app/stores";
</script>

<div class="footer">
  <div class="footer-social">
    <ul>
      <li><a href="https://www.youtube.com/c/MarioKartCentral" rel="external" title="YouTube">▶️</a></li>
      <li><a href="https://twitter.com/mk_central" rel="external" title="Twitter">🐦</a></li>
      <li><a href="https://www.twitch.tv/mariokartcentral" rel="external" title="Twitch">🗨️</a></li>
    </ul>
  </div>
  <div class="footer-terms">
    <a href="/{$page.params.lang}/user/terms">Terms and Rules</a>
  </div>
  <div class="footer-privacy">
    <a href="/{$page.params.lang}/user/privacy-policy">Privacy Policy</a>
  </div>
  <div class="footer-copyright">&copy; 2018-2025 mkcentral.com Mario Kart&trade; and &copy; Nintendo.</div>
</div>

<style>
  .footer {
    display: flex;
    background-color: #313030;
    font-size: 14px;
    gap: 15px;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    padding: 5px;
  }
  .footer-social {
    flex: 1;
  }
  .footer-social ul {
    display: flex;
    list-style: none;
  }

  a {
    text-decoration: none;
  }
</style>
