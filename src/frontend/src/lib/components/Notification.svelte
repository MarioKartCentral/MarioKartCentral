<script lang="ts">
  import type { Notification } from '$lib/types/notification';
  import { onMount } from 'svelte';
  import { have_unread_notification } from '$lib/stores/stores';
  import DropdownMenu from './DropdownMenu.svelte';
  import Dropdown from './common/Dropdown.svelte';
  import DropdownItem from './common/DropdownItem.svelte';
  import LL from '$i18n/i18n-svelte';
  import { goto } from '$app/navigation';
  import NotificationContent from './common/NotificationContent.svelte';
  import { DropdownDivider, DropdownHeader } from 'flowbite-svelte';

  let dropdown: DropdownMenu;
  export function toggleNotificationMenu() {
    dropdown.toggleDropdown();
  }

  let notifications: Notification[] = [];
  $: {
    have_unread_notification.set(notifications.filter((n) => !n.is_read).length);
  }
  $: hasUnread = notifications.some(n => !n.is_read);

  let isInitialLoad = true;
  have_unread_notification.subscribe(() => {
    // This is to sync the notifications whenever the user is on the /notifications
    // page and decides to mark a notification as read/unread
    if (!isInitialLoad)
      fetchUnreadNotifications();
    isInitialLoad = false;
  })

  onMount(() => {
    fetchUnreadNotifications();
  });
  
  async function fetchUnreadNotifications() {
    const res = await fetch('/api/notifications/list?is_read=0');
    if (res.status !== 200) {
      return;
    }
    const body = (await res.json()) as Notification[];
    notifications = body;
  }

  async function makeNotificationAsRead(id: number) {
    const res = await fetch(`/api/notifications/edit/read_status/${id}`, {
      method: 'POST',
      body: JSON.stringify({ is_read: true }),
    });
    if (res.status !== 200) {
      return;
    }
    const body = await res.json();
    if (body.count > 0) {
      notifications = notifications.map((n) => ({
        ...n,
        is_read: n.id === id ? true : n.is_read,
      }));
    }
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
  }

  async function handleClick(id: number, link: string) {
    await makeNotificationAsRead(id)
    goto(link)
  }
</script>

<Dropdown>
  <div class="wrapper">
    {#if notifications.length === 0}
      <DropdownHeader divClass="py-2 px-4 text-white">{$LL.NOTIFICATION.NO_UNREAD()}</DropdownHeader>
    {/if}
    {#each notifications as { id, type, content_id, content_args, link, created_date, is_read}}
      <DropdownItem on:click={(e) => {console.log(e.target); handleClick(id, link)}}>
        <NotificationContent {type} {content_id} {content_args} {created_date} {is_read}/>
      </DropdownItem>
      <DropdownDivider divClass="my-1 h-px bg-gray-500 dark:bg-gray-600"/>
    {/each}
    <DropdownItem href="/notifications">{$LL.NOTIFICATION.SEE_ALL_NOTIFICATIONS()}</DropdownItem>
    {#if hasUnread}
      <DropdownDivider divClass="my-1 h-px bg-gray-500 dark:bg-gray-600"/>
      <DropdownItem on:click={makeAllNotificationsAsRead}>{$LL.NOTIFICATION.MARK_ALL_READ()}</DropdownItem>
    {/if}
  </div>
</Dropdown>

<style>
  .wrapper {
    max-width: 400px;
  }
</style>