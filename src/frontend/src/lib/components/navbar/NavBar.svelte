<script lang="ts">
  import { page } from '$app/stores';
  import LL from '$i18n/i18n-svelte';
  import { user, have_unread_notification } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import Notification from './Notification.svelte';
  import ModPanel from './ModPanel.svelte';
  import { mod_panel_permissions } from '$lib/util/permissions';
  import { Navbar, NavBrand, Avatar } from 'flowbite-svelte';
  import NavHamburger from './NavHamburger.svelte';
  import NavLi from './NavLi.svelte';
  import NavUlist from './NavUlist.svelte';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import { ChevronDownOutline, BellSolid, BellOutline } from 'flowbite-svelte-icons';
  import AlertCount from '$lib/components/common/AlertCount.svelte';
  import { check_permission, series_permissions } from '$lib/util/permissions';
  import LoginRegister from '$lib/components/login/LoginRegister.svelte';
  import LanguagePicker from '$lib/components/navbar/LanguagePicker.svelte';
  
  let notify: Notification;

  let user_info: UserInfo;
  let unread_count = 0;
  let mod_action_count = 0;

  let avatar_url = '';

  let menu_hidden = true;

  $: is_mod = mod_panel_permissions.some((p) => check_permission(user_info, p));

  user.subscribe((value) => {
    user_info = value;
    if (user_info.player?.user_settings && user_info.player?.user_settings.avatar) {
      avatar_url = user_info.player.user_settings.avatar;
    }
    let mod_notifs = value.mod_notifications;
    if(mod_notifs) {
      mod_action_count = Object.values(mod_notifs).reduce((sum, a) => sum + a, 0);
    }
  });
  have_unread_notification.subscribe((value) => {
    unread_count = value;
  });

  async function logout() {
      const response = await fetch('/api/user/logout', { method: 'POST' });
      if (response.status < 300) {
        window.location.href = `/${$page.params.lang}/`;
      } else {
        alert($LL.LOGIN.LOGOUT_FAILED());
    }
  }
</script>

<Navbar fluid={true} class="bg-primary-800">
  <div class="flex gap-2 items-center">
    <NavHamburger bind:menu_hidden={menu_hidden}/>
    <NavBrand href="/{$page.params.lang}">
      <span class="text-white text-2xl font-bold desktop:text-3xl">MKCentral</span>
    </NavBrand>
  </div>
  <div class="flex items-center desktop:order-2">
    <div class="nav-user-bar cursor-pointer">
      <LanguagePicker/>
    </div>
    <div class="nav-user-bar cursor-pointer relative">
      {#if unread_count}
        <BellSolid size="lg" class="text-yellow-400"/>
        <AlertCount count={unread_count} placement="top-right"/>
      {:else}
        <BellOutline size="lg" class="text-gray-300"/>
      {/if}
    </div>
    <Notification bind:this={notify} />
    {#if user_info.is_checked}
      {#if user_info.player}
        <div class="flex items-center cursor-pointer nav-user-bar font-bold">
          <Avatar size='sm' src={avatar_url}/>
          <div class="username hidden sm:block">
            {user_info.player.name}
          </div>
        </div>
        <Dropdown>
          <DropdownItem href="/{$page.params.lang}/registry/players/profile?id={user_info.player_id}">{$LL.NAVBAR.PROFILE()}</DropdownItem>
          <DropdownItem href="/{$page.params.lang}/registry/players/edit-profile">{$LL.PLAYERS.PROFILE.EDIT_PROFILE()}</DropdownItem>
          <DropdownItem href="/{$page.params.lang}/registry/invites">{$LL.PLAYERS.PROFILE.INVITES()}</DropdownItem>
          {#if user_info.token_count}
            <DropdownItem href="/{$page.params.lang}/user/api-tokens">{$LL.API_TOKENS.API_TOKENS()}</DropdownItem>
          {/if}
          <DropdownItem on:click={logout}><span class="logout">{$LL.LOGIN.LOGOUT()}</span></DropdownItem>
        </Dropdown>
      {:else if user_info.id !== null}
        <div class="flex items-center cursor-pointer nav-user-bar font-bold">
          <Avatar size='sm'/>
        </div>
        <Dropdown>
          {#if user_info.email_confirmed}
            <DropdownItem href="/{$page.params.lang}/user/player-signup">{$LL.NAVBAR.PLAYER_SIGNUP()}</DropdownItem>
          {:else}
            <DropdownItem href="/{$page.params.lang}/user/confirm-email">{$LL.LOGIN.CONFIRM_EMAIL()}</DropdownItem>
          {/if}
          {#if user_info.token_count}
            <DropdownItem href="/{$page.params.lang}/user/api-tokens">{$LL.API_TOKENS.API_TOKENS()}</DropdownItem>
          {/if}
          <DropdownItem on:click={logout}><span class="logout">{$LL.LOGIN.LOGOUT()}</span></DropdownItem>
        </Dropdown>
      {:else}
        <div class="flex items-center cursor-pointer nav-user-bar font-bold">
          <Avatar size='sm'/>
        </div>
        <Dropdown>
          <LoginRegister/>
        </Dropdown>
      {/if}
    {/if}
  </div>
  
  <NavUlist bind:menu_hidden={menu_hidden}>
    <NavLi nav_name="REGISTRY" has_dropdown>
      {$LL.NAVBAR.REGISTRY()}
      <ChevronDownOutline class="inline"/>
    </NavLi>
    <Dropdown>
      <DropdownItem href="/{$page.params.lang}/registry/players">{$LL.NAVBAR.PLAYERS()}</DropdownItem>
      <DropdownItem href="/{$page.params.lang}/registry/teams">{$LL.NAVBAR.TEAMS()}</DropdownItem>
      <DropdownItem href="/{$page.params.lang}/registry/teams/transfers">{$LL.NAVBAR.RECENT_TRANSCATIONS()}</DropdownItem>
    </Dropdown>
    <NavLi nav_name="TOURNAMENTS" has_dropdown>
      {$LL.NAVBAR.TOURNAMENTS()}
      <ChevronDownOutline class="inline"/>
    </NavLi>
    <Dropdown>
      <DropdownItem href="/{$page.params.lang}/tournaments">{$LL.NAVBAR.TOURNAMENT_LISTING()}</DropdownItem>
      <DropdownItem href="/{$page.params.lang}/tournaments/series">{$LL.NAVBAR.TOURNAMENT_SERIES()}</DropdownItem>
      {#if check_permission(user_info, series_permissions.create_tournament_template)}
        <DropdownItem href="/{$page.params.lang}/tournaments/templates">{$LL.NAVBAR.TOURNAMENT_TEMPLATES()}</DropdownItem>
      {/if}
    </Dropdown>
    <NavLi href="/{$page.params.lang}/time-trials" nav_name="TIME TRIALS">{$LL.NAVBAR.TIME_TRIALS()}</NavLi>
    <NavLi href="/{$page.params.lang}/lounge" nav_name="LOUNGE">{$LL.NAVBAR.LOUNGE()}</NavLi>
    
    <NavLi has_dropdown>
      {$LL.NAVBAR.DISCORD()}
      <ChevronDownOutline class="inline"/>
    </NavLi>
    <Dropdown>
      <DropdownItem href="https://discord.gg/Pgd8xr6" target="_blank">Site Discord</DropdownItem>
      <DropdownItem href="https://discord.gg/Q9HCD8tVvD" target="_blank">MKWorld</DropdownItem>
      <DropdownItem href="https://discord.gg/HuE4Pd8Skf" target="_blank">MK8DX</DropdownItem>
      <DropdownItem href="https://discord.gg/H3Nsdcn" target="_blank">MKTour</DropdownItem>
      <DropdownItem href="https://discord.gg/f9J3RNWmQ9" target="_blank">MKWii</DropdownItem>
    </Dropdown>
    {#if is_mod}
      <NavLi nav_name="MODERATOR" has_dropdown>
        {$LL.NAVBAR.MODERATOR()}
        {#if mod_action_count}
          <AlertCount count={mod_action_count}/>
        {/if}
        <ChevronDownOutline class="inline"/>
      </NavLi>
      <ModPanel/>
    {/if}
  </NavUlist>
</Navbar>

<style>
  .username {
    color: white;
    padding-left: 10px;
    text-overflow: ellipsis;
    max-width: 100px;
    text-wrap: nowrap;
    overflow: hidden;
  }
  .nav-user-bar {
    margin-left: 10px;
    margin-right: 10px;
  }
  .logout {
    color: rgb(255, 44, 44);
  }
</style>
