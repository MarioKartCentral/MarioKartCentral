<script lang="ts">
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import NavBarItem from "./NavBarItem.svelte";
  import logo from '$lib/assets/logo.png';
</script>

<nav>
  <div class="nav-brand">
    <a href="/{$page.params.lang}" title="Home Page">
      <img src={logo} width="120px" alt="MKCentral Logo" />
    </a>
  </div>
  <div class="nav-main">
    <ul>
      <NavBarItem selected={$page.data.activeNavItem==="TOURNAMENTS"} href="/{$page.params.lang}/tournaments">{@html $LL.NAVBAR.TOURNAMENTS()}</NavBarItem>
      <NavBarItem selected={$page.data.activeNavItem==="TIME TRIALS"} href="/{$page.params.lang}/time-trials">{@html $LL.NAVBAR.TIME_TRIALS()}</NavBarItem>
      <NavBarItem selected={$page.data.activeNavItem==="LOUNGE"} href="/{$page.params.lang}/lounge">{@html $LL.NAVBAR.LOUNGE()}</NavBarItem>
      <NavBarItem selected={$page.data.activeNavItem==="REGISTRY"} href="/{$page.params.lang}/registry">{@html $LL.NAVBAR.REGISTRY()}</NavBarItem>
      <NavBarItem external="http://discord.gg/Pgd8xr6">{@html $LL.NAVBAR.DISCORD()}</NavBarItem>
    </ul>
  </div>
  <div class="nav-options">
    <ul>
      <NavBarItem title="Notifications" href="#">🔔</NavBarItem>
      <NavBarItem title="Language Picker" href="#">🌐</NavBarItem>
      <NavBarItem title="Profile" href="#">👤</NavBarItem>
    </ul>
  </div>
</nav>

<style>
  nav {
    display: flex;
    background-color: #5CE49A;
    color: white;
    height: 40px;
  }

  .nav-brand {
    background-color: #31D682;
    display: flex;
    align-items: center;
    box-shadow: 2px 0 8px #141414;
  }

  .nav-brand img {
    padding: 5px 10px;
  }

  .nav-main {
    width: max-content;
    flex: 1;
    display: flex;
    align-items: center;
  }

  .nav-main ul {
    display: flex;
    align-items: stretch;
    padding: 0px 20px;
    gap: 30px;
    list-style: none;
  }

  .nav-options {
    background-color: #31D682;
    display: flex;
    align-items: center;
    box-shadow: -2px 0 8px #141414;
  }

  .nav-options ul {
    display: flex;
    align-items: stretch;
    list-style: none;
    padding: 0px 10px;
    gap: 10px;
  }
</style>