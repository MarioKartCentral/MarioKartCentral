<script lang="ts">
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import NavBarItem from './NavBarItem.svelte';
  import logo from '$lib/assets/logo.png';
  import { user, have_unread_notification } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import Notification from './Notification.svelte';
  import ModPanel from './ModPanel.svelte';
  import { mod_panel_permissions } from '$lib/util/util';

  let notify: Notification;
  let mod_panel: ModPanel;

  let user_info: UserInfo;
  let have_unread = false;

  let opened = false;

  user.subscribe((value) => {
    user_info = value;
  });
  have_unread_notification.subscribe((value) => {
    have_unread = value;
  });
</script>

<nav>
  <div class="nav-top-wrap">
    <div class="nav-brand">
      <a href="/{$page.params.lang}" title={$LL.NAVBAR.HOME_PAGE()}>
        <img src={logo} width="120px" alt="MKCentral Logo" />
      </a>
    </div>
    <button
      class="nav-menu-icon"
      on:click|stopPropagation={() => {
        opened = !opened;
        console.log(opened);
      }}
    >
      {$LL.NAVBAR.MENU()}
    </button>
  </div>
  <div class="nav-main" class:nav-closed={!opened}>
    <ul>
      <NavBarItem selected={$page.data.activeNavItem === 'TOURNAMENTS'} href="/{$page.params.lang}/tournaments"
        >{$LL.NAVBAR.TOURNAMENTS()}</NavBarItem
      >
      <NavBarItem selected={$page.data.activeNavItem === 'TIME TRIALS'} href="/{$page.params.lang}/time-trials"
        >{$LL.NAVBAR.TIME_TRIALS()}</NavBarItem
      >
      <NavBarItem selected={$page.data.activeNavItem === 'LOUNGE'} href="/{$page.params.lang}/lounge"
        >{$LL.NAVBAR.LOUNGE()}</NavBarItem
      >
      <NavBarItem selected={$page.data.activeNavItem === 'REGISTRY'} href="/{$page.params.lang}/registry"
        >{$LL.NAVBAR.REGISTRY()}</NavBarItem
      >
      <NavBarItem external="http://discord.gg/Pgd8xr6">{$LL.NAVBAR.DISCORD()}</NavBarItem>
      {#if user_info.permissions.some((p) => mod_panel_permissions.includes(p))}
        <NavBarItem title="Moderator">
          <button on:click|stopPropagation={mod_panel.toggleModPanel}> {$LL.NAVBAR.MODERATOR()} </button>
          <ModPanel bind:this={mod_panel} />
        </NavBarItem>
      {/if}
    </ul>
  </div>
  <div class="nav-options" class:nav-closed={!opened}>
    <ul>
      <NavBarItem title={$LL.NAVBAR.NOTIFICATIONS()}>
        <button on:click|stopPropagation={notify.toggleNotificationMenu}>
          🔔{#if have_unread}🔴{/if}
        </button>
        <Notification bind:this={notify} />
      </NavBarItem>
      <NavBarItem title={$LL.NAVBAR.LANGUAGE_PICKER()} href="#">🌐</NavBarItem>
      {#if user_info.player}
        <NavBarItem
          title={$LL.NAVBAR.PROFILE()}
          href="/{$page.params.lang}/registry/players/profile?id={user_info.player_id}"
          >👤
          {user_info.player.name}
        </NavBarItem>
      {:else if user_info.id !== null}
        <NavBarItem title={$LL.NAVBAR.PLAYER_SIGNUP()} href="/{$page.params.lang}/player-signup"
          >{$LL.NAVBAR.PLAYER_SIGNUP()}</NavBarItem
        >
      {:else}
        <NavBarItem title={$LL.NAVBAR.LOGIN()} href="/{$page.params.lang}/login">{$LL.NAVBAR.LOGIN()}</NavBarItem>
        <NavBarItem title={$LL.NAVBAR.REGISTER()} href="/{$page.params.lang}/register"
          >{$LL.NAVBAR.REGISTER()}</NavBarItem
        >
      {/if}
    </ul>
  </div>
</nav>

<style>
  nav {
    display: flex;
    flex-direction: column;
    width: 100%;
    padding: 0;
    color: white;
    background-color: #5ce49a;
  }

  .nav-top-wrap {
    flex-basis: 40px;
    height: 40px;
    align-items: center;
    display: flex;
    justify-content: space-between;
    background-color: #31d682;
  }

  .nav-brand {
    background-color: #31d682;
    align-items: center;
    text-align: left;
    width: 100%;
  }

  .nav-brand img {
    padding: 5px 10px;
  }

  .nav-menu-icon {
    margin-right: 20px;
    cursor: pointer;
  }

  .nav-closed {
    display: none;
  }

  .nav-main {
    background-color: #5ce49a;
  }

  .nav-main ul {
    display: flex;
    flex-direction: column;
    list-style: none;
    margin-left: 10px;
    gap: 0px;
  }

  .nav-options {
    background-color: #31d682;
  }

  .nav-options ul {
    display: flex;
    flex-direction: column;
    list-style: none;
    margin-left: 10px;
    gap: 0px;
  }

  /* desktop */
  @media (min-width: 1024px) {
    nav {
      flex-direction: row;
    }

    .nav-top-wrap {
      /* reset flex to default */
      flex: 0 1 auto;
    }

    .nav-menu-icon {
      display: none;
    }

    .nav-main {
      flex-grow: 1;
      display: flex;
      align-items: center;
    }

    .nav-main ul {
      margin-left: 20px;
      flex-direction: row;
      gap: 30px;
    }

    .nav-options {
      display: flex;
      align-items: center;
      box-shadow: -2px 0 8px #141414;
    }

    .nav-options ul {
      flex-direction: row;
      gap: 10px;
      margin-left: 20px;
      margin-right: 20px;
    }
  }
</style>
