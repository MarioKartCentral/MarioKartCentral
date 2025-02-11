<script lang="ts">
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import logo from '$lib/assets/logo.png';
  import { user, have_unread_notification } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import Notification from './Notification.svelte';
  import ModPanel from './ModPanel.svelte';
  import { mod_panel_permissions } from '$lib/util/permissions';
  import { Navbar, NavBrand, NavUl, NavLi, NavHamburger, Avatar, Button } from 'flowbite-svelte';
  import Dropdown from './common/Dropdown.svelte';
  import DropdownItem from './common/DropdownItem.svelte';
  import { ChevronDownOutline, ChevronDownSolid, BellSolid, BellOutline, GlobeSolid } from 'flowbite-svelte-icons';
  import AlertCount from './common/AlertCount.svelte';
  import { check_permission, series_permissions } from '$lib/util/permissions';
  import LoginRegister from './common/LoginRegister.svelte';
  
  let notify: Notification;

  let user_info: UserInfo;
  let unread_count = 0;

  let avatar_url = '';

  user.subscribe((value) => {
    user_info = value;
    if (user_info.player?.user_settings && user_info.player?.user_settings.avatar) {
      avatar_url = user_info.player.user_settings.avatar;
    }
  });
  have_unread_notification.subscribe((value) => {
    unread_count = value;
  });

  // underline a nav item if it's the section we're currently in
  function checkSelectedNav(name: string) {
    if($page.data.activeNavItem === name) {
      return "text-white font-bold underline underline-offset-4";
    }
    return "";
  }

  async function logout() {
      const response = await fetch('/api/user/logout', { method: 'POST' });

      if (response.status < 300) {
        window.location.reload();
      } else {
        alert($LL.LOGIN.LOGOUT_FAILED());
    }
  }

</script>

<Navbar fluid={true} class="bg-primary-800" >
    <NavBrand href="/{$page.params.lang}">
      <img src={logo} width="120px" alt="MKCentral Logo" />
    </NavBrand>
    <div class="flex items-center md:order-2">
      <div class="nav-user-bar cursor-pointer relative">
        {#if unread_count}
          <BellSolid size="xl" class="text-yellow-400"/>
          <AlertCount count={unread_count} placement="top-right"/>
        {:else}
          <BellOutline size="xl" class="text-gray-300"/>
        {/if}
        
      </div>
      <Notification bind:this={notify} />
      <div class="nav-user-bar cursor-pointer">
        <GlobeSolid size="xl" class="text-gray-300"/>
      </div>
      {#if user_info.player}
        <div class="flex items-center cursor-pointer nav-user-bar font-bold">
          <Avatar size='sm' src={avatar_url}/>
          <div class="username">
            {user_info.player.name}
          </div>
        </div>
        <Dropdown>
          <DropdownItem href="/{$page.params.lang}/registry/players/profile?id={user_info.player_id}">{$LL.NAVBAR.PROFILE()}</DropdownItem>
          <DropdownItem href="/{$page.params.lang}/registry/players/edit-profile">{$LL.PLAYERS.PROFILE.EDIT_PROFILE()}</DropdownItem>
          <DropdownItem href="/{$page.params.lang}/registry/invites">{$LL.PLAYERS.PROFILE.INVITES()}</DropdownItem>
          <DropdownItem on:click={logout}><span class="logout">{$LL.LOGIN.LOGOUT()}</span></DropdownItem>
        </Dropdown>
      {:else if user_info.id !== null}
        <Button size="sm">
          {$LL.NAVBAR.ACCOUNT()}
          <ChevronDownSolid class="w-3 h-3 ms-2 text-white dark:text-white" />
        </Button>
        <Dropdown>
          <DropdownItem href="/{$page.params.lang}/player-signup">{$LL.NAVBAR.PLAYER_SIGNUP()}</DropdownItem>
          <DropdownItem on:click={logout}><span class="logout">{$LL.LOGIN.LOGOUT()}</span></DropdownItem>
        </Dropdown>
      {:else}
        <Button size="sm">
          {$LL.NAVBAR.LOGIN_REGISTER()}
          <ChevronDownSolid class="w-3 h-3 ms-2 text-white dark:text-white" />
        </Button>
        <Dropdown>
          <LoginRegister/>
        </Dropdown>
      {/if}
      <NavHamburger/>
    </div>
    
    <NavUl classUl="bg-primary-800 border-none" nonActiveClass='text-white font-bold'>
      <NavLi class="cursor-pointer {checkSelectedNav('TOURNAMENTS')}">
        <a href="/{$page.params.lang}/tournaments">{$LL.NAVBAR.TOURNAMENTS()}</a>
        <ChevronDownOutline class="inline"/>
      </NavLi>
      <Dropdown>
        <DropdownItem href="/{$page.params.lang}/tournaments">{$LL.NAVBAR.TOURNAMENT_LISTING()}</DropdownItem>
        <DropdownItem href="/{$page.params.lang}/tournaments/series">{$LL.NAVBAR.TOURNAMENT_SERIES()}</DropdownItem>
        {#if check_permission(user_info, series_permissions.create_tournament_template)}
          <DropdownItem href="/{$page.params.lang}/tournaments/templates">{$LL.NAVBAR.TOURNAMENT_TEMPLATES()}</DropdownItem>
        {/if}
      </Dropdown>
      <NavLi href="/{$page.params.lang}/time-trials" class={checkSelectedNav('TIME TRIALS')}>{$LL.NAVBAR.TIME_TRIALS()}</NavLi>
      <NavLi href="/{$page.params.lang}/lounge" class={checkSelectedNav('LOUNGE')}>{$LL.NAVBAR.LOUNGE()}</NavLi>
      <NavLi class="cursor-pointer {checkSelectedNav('REGISTRY')}">
        {$LL.NAVBAR.REGISTRY()}
        <ChevronDownOutline class="inline"/>
      </NavLi>
      <Dropdown>
        <DropdownItem href="/{$page.params.lang}/registry/players">{$LL.NAVBAR.PLAYERS()}</DropdownItem>
        <DropdownItem href="/{$page.params.lang}/registry/teams">{$LL.NAVBAR.TEAMS()}</DropdownItem>
        <DropdownItem href="/{$page.params.lang}/registry/teams/transfers">{$LL.NAVBAR.RECENT_TRANSCATIONS()}</DropdownItem>
      </Dropdown>
      <NavLi href="http://discord.gg/Pgd8xr6">{$LL.NAVBAR.DISCORD()}</NavLi>
      {#if mod_panel_permissions.some((p) => check_permission(user_info, p))}
        <ModPanel/>
      {/if}
    </NavUl>
</Navbar>

<style>
  .username {
    color: white;
    padding-left: 10px;
  }
  .nav-user-bar {
    margin-left: 10px;
    margin-right: 10px;
  }
  .logout {
    color: rgb(255, 44, 44);
  }
</style>
