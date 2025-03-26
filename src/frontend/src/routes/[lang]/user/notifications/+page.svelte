<script lang="ts">
  import type { Notification } from '$lib/types/notification';
  import Section from "$lib/components/common/Section.svelte";
  import LL from '$i18n/i18n-svelte';
  import PageNavigation from "$lib/components/common/PageNavigation.svelte";
  import NotificationContent from "$lib/components/common/NotificationContent.svelte";
  import { goto } from "$app/navigation";
  import Button from "$lib/components/common/buttons/Button.svelte";
  import { have_unread_notification, user } from "$lib/stores/stores";
  import { DotsVerticalOutline } from "flowbite-svelte-icons";
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from "$lib/components/common/DropdownItem.svelte";
  import type { UserInfo } from "$lib/types/user-info";

  const maxNotificationsPerPage = 50;
  const dropdownOpenStatus: { [key: string]: boolean } = {};
  let notifications: Notification[] = [];
  let currentPage = 1;
  let isInitialLoad = true;

  // subscribing to have_unread_notification syncs notifications with the navbar notifications
  have_unread_notification.subscribe((val) => {
    if (!isInitialLoad && val === 0) {
      notifications = notifications.map((n) => ({
        ...n,
        is_read: true,
      }));
    }
    isInitialLoad = false;
  })

  // subscribing to user store allows us to only fetch notifications if the user is logged in
  let user_info: UserInfo;
  user.subscribe((value) => {
      user_info = value;
  });
  $: user_info?.id !== null && fetchNotifications();

  $: pageCount = Math.ceil(notifications.length / maxNotificationsPerPage)
  $: notificationList = notifications.slice((currentPage-1)*maxNotificationsPerPage, currentPage*maxNotificationsPerPage)
  $: hasUnread = notifications.some(n => !n.is_read)
  $: isLoggedIn = user_info.id !== null

  async function fetchNotifications() {
    const res = await fetch('/api/notifications/list');
    if (res.status === 200) {
      notifications = await res.json();
    }
  }

  async function changeReadStatus(id: number, isRead: boolean) {
    const res = await fetch(`/api/notifications/edit/read_status/${id}`, {
      method: 'POST',
      body: JSON.stringify({ is_read: isRead }),
    });
    if (res.status !== 200) {
      return;
    }
    const body = await res.json();
    if (body.count > 0) {
      notifications = notifications.map((n) => ({
        ...n,
        is_read: n.id === id ? isRead : n.is_read,
      }));
    }
    have_unread_notification.update((n) => !isRead ? n+1 : n-1);
  }

  async function makeAllNotificationsAsRead() {
    const res = await fetch(`/api/notifications/edit/read_status/all`, {
      method: 'POST',
      body: JSON.stringify({ is_read: true }),
    });
    if (res.status !== 200) {
      return;
    }
    const body = await res.json();
    if (body.update_count > 0) {
      notifications = notifications.map((n) => ({
        ...n,
        is_read: true,
      }));
    }
    have_unread_notification.set(0);
  }

  function handleChangeStatus(id: number, is_read: boolean) {
    changeReadStatus(id, !is_read)
    dropdownOpenStatus[id] = false
  }

  async function handleClick(id: number, link: string) {
    await changeReadStatus(id, true)
    goto(link)
  }
</script>

<svelte:head>
  <title>Notifications | Mario Kart Central</title>
</svelte:head>

{#if user_info.is_checked}
  {#if !isLoggedIn}
    {$LL.NOTIFICATION.MUST_BE_LOGGED_IN()}
  {:else}
    <Section header={$LL.NAVBAR.NOTIFICATIONS()}>
      <div slot="header_content">
        {#if hasUnread}
          <Button on:click={makeAllNotificationsAsRead}>{$LL.NOTIFICATION.MARK_ALL_READ()}</Button>
        {/if}
      </div>
      <div class="notification-count">
        <PageNavigation bind:currentPage={currentPage} bind:totalPages={pageCount} refresh_function={() => {}}/>
        {notifications.length} {$LL.NAVBAR.NOTIFICATIONS()}
      </div>
      {#if notifications.length}
        <div class="my-1 h-px bg-gray-500 dark:bg-gray-600"></div>
      {/if}
      {#each notificationList as { id, type, content_id, content_args, link, created_date, is_read}}
        <button class="content-wrapper hover:bg-primary-700" on:click={() => handleClick(id, link)}>
          <NotificationContent {type} {content_id} {content_args} {created_date} {is_read}/>
        </button>
        <button>
          <DotsVerticalOutline class="hover:text-yellow-300"/>
          <Dropdown bind:open={dropdownOpenStatus[id]}>
            <DropdownItem on:click={() => handleChangeStatus(id, is_read)}>{is_read ? $LL.NOTIFICATION.MARK_UNREAD() : $LL.NOTIFICATION.MARK_READ()}</DropdownItem>
          </Dropdown>
        </button>
        <div class="my-1 h-px bg-gray-500 dark:bg-gray-600"></div>
      {/each}
      <PageNavigation bind:currentPage={currentPage} bind:totalPages={pageCount} refresh_function={() => {}}/>
    </Section>
  {/if}
{/if}

<style>
  .notification-count {
    margin: 10px 0px;
  }
  .content-wrapper {
    width: calc(100% - 25px);
    padding: 10px;
  }
</style>