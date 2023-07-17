<script lang="ts">
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import NavBarItem from './NavBarItem.svelte';
  import logo from '$lib/assets/logo.png';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import type { Notification } from '$lib/types/notification';
  import { onMount } from 'svelte';

  let user_info: UserInfo;
  let notifications: Notification[] = [];
  $: have_unread = notifications.some((n) => !n.is_read);

  user.subscribe((value) => {
    user_info = value;
  });

  let is_notification_menu_activated = false;

  onMount(async () => {
    const res = await fetch('/api/notifications/list?is_read=0');
    if (res.status != 200) {
      return;
    }
    const body = (await res.json()) as Notification[];
    notifications = body;
  });

  function toggleNotificationMenu() {
    is_notification_menu_activated = !is_notification_menu_activated;
  }
</script>

<nav>
  <div class="nav-brand">
    <a href="/{$page.params.lang}" title="Home Page">
      <img src={logo} width="120px" alt="MKCentral Logo" />
    </a>
  </div>
  <div class="nav-main">
    <ul>
      <NavBarItem selected={$page.data.activeNavItem === 'TOURNAMENTS'} href="/{$page.params.lang}/tournaments"
        >{@html $LL.NAVBAR.TOURNAMENTS()}</NavBarItem
      >
      <NavBarItem selected={$page.data.activeNavItem === 'TIME TRIALS'} href="/{$page.params.lang}/time-trials"
        >{@html $LL.NAVBAR.TIME_TRIALS()}</NavBarItem
      >
      <NavBarItem selected={$page.data.activeNavItem === 'LOUNGE'} href="/{$page.params.lang}/lounge"
        >{@html $LL.NAVBAR.LOUNGE()}</NavBarItem
      >
      <NavBarItem selected={$page.data.activeNavItem === 'REGISTRY'} href="/{$page.params.lang}/registry"
        >{@html $LL.NAVBAR.REGISTRY()}</NavBarItem
      >
      <NavBarItem external="http://discord.gg/Pgd8xr6">{@html $LL.NAVBAR.DISCORD()}</NavBarItem>
    </ul>
  </div>
  <div class="nav-options">
    <ul>
      <NavBarItem title="Notifications" clickable on:click={toggleNotificationMenu}>
        🔔
        {#if have_unread}
          🔴
        {/if}
      </NavBarItem>
      <NavBarItem title="Language Picker" href="#">🌐</NavBarItem>
      {#if user_info.player_id !== null}
        <NavBarItem title="Profile" href="#"
          >👤
          {user_info.name}
        </NavBarItem>
      {:else if user_info.id !== null}
        <NavBarItem title="Player Signup" href="/{$page.params.lang}/player-signup">Player Signup</NavBarItem>
      {:else}
        <NavBarItem title="Login" href="/{$page.params.lang}/login">Login</NavBarItem>
        <NavBarItem title="Register" href="/{$page.params.lang}/register">Register</NavBarItem>
      {/if}
    </ul>
  </div>
  {#if is_notification_menu_activated}
    <div class="nav-drop-down">
      <div class="nav-drop-down-container">
        <ul>
          {#each notifications as { id, content, created_date, is_read, type }}
            <li>
              <div class="nav-drop-down-item">
                {content}
                <span>{new Date((created_date || 0) * 1000).toLocaleString()}</span>
                <button>☑</button>
              </div>
            </li>
          {/each}
        </ul>
      </div>
    </div>
  {/if}
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

  .nav-drop-down {
    position: fixed;
    top: 40px;
    right: 0;
    width: 400px;
    z-index: 100;
  }

  .nav-drop-down-container {
    background-color: #5CE49A;
    color: white;
    /* padding: 10px; */
    box-shadow: 0 0 8px #141414;
  }

  .nav-drop-down-container ul {
    list-style: none;
    padding: 0;
  }

  .nav-drop-down-item {
    border-bottom: 1px solid #f2f2f2;
  }
</style>
