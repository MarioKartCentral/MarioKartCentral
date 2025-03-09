<script lang="ts">
  import type { Notification } from '$lib/types/notification';
  import { have_unread_notification, user } from '$lib/stores/stores';
  // import DropdownMenu from './DropdownMenu.svelte';
  import Dropdown from '$lib/components/common/Dropdown.svelte';
  import DropdownItem from '$lib/components/common/DropdownItem.svelte';
  import LL from '$i18n/i18n-svelte';
  import { goto } from '$app/navigation';
  import NotificationContent from '$lib/components/common/NotificationContent.svelte';
  import { DropdownDivider, DropdownHeader } from 'flowbite-svelte';
  import type { UserInfo } from '$lib/types/user-info';

  const maxBellNotifications = 5;
  // let dropdown: DropdownMenu;
  // export function toggleNotificationMenu() {
  //   dropdown.toggleDropdown();
  // }

  let notifications: Notification[] = [];
  $: {
    have_unread_notification.set(notifications.filter((n) => !n.is_read).length);
  }
  $: hasUnread = notifications.some(n => !n.is_read);

  // subscribing to have_unread_notification syncs with notifications in the /notifications page
  let fetchCount = 0;
  have_unread_notification.subscribe(() => {
    if (fetchCount > 1) // ignore initial sub and initial user_info sub
      fetchUnreadNotifications();
    fetchCount++;
  })

  // subscribing to user allows us to only fetch notifications if the user is logged in
  let user_info: UserInfo;
  user.subscribe((value) => {
      user_info = value;
  });
  $: user_info.id !== null && fetchUnreadNotifications();
  
  async function fetchUnreadNotifications() {
    const res = await fetch('/api/notifications/list?is_read=0');
    if (res.status !== 200) {
      return;
    }
    notifications = await res.json()
    if (notifications.length === 0)
      fetchCount++; // increment since have_unread_notification.subscribe won't trigger if 0 notifs
  }

  async function makeNotificationAsRead(id: number) {
    const res = await fetch(`/api/notifications/edit/read_status/${id}`, {
      method: 'POST',
      body: JSON.stringify({ is_read: true }),
    });
    if (res.status !== 200) {
      return;
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
    notifications = []
  }

  async function handleClick(id: number, link: string) {
    await makeNotificationAsRead(id)
    goto(link)
  }
</script>

<Dropdown>
  <div class="wrapper">
    {#if notifications.length === 0}
      <DropdownHeader divClass="py-2 px-4 text-white"><div class="text-center">{$LL.NOTIFICATION.NO_UNREAD()}</div></DropdownHeader>
    {/if}
    {#each notifications as { id, type, content_id, content_args, link, created_date, is_read}, idx}
      {#if idx < maxBellNotifications}
        <DropdownItem on:click={() => handleClick(id, link)}>
          <NotificationContent {type} {content_id} {content_args} {created_date} {is_read}/>
        </DropdownItem>
        {#if idx === maxBellNotifications - 1 && notifications.length > maxBellNotifications}
          <p class="extra-count">
            <DropdownDivider divClass="w-3/5 my-1 h-px bg-gray-500 dark:bg-gray-600"/>
            +{notifications.length - maxBellNotifications} more
          </p>
        {/if}
        <DropdownDivider divClass="my-1 h-px bg-gray-500 dark:bg-gray-600"/>
      {/if}
    {/each}
    <DropdownItem href="/notifications"><div class="text-center">{$LL.NOTIFICATION.SEE_ALL_NOTIFICATIONS()}</div></DropdownItem>
    {#if hasUnread}
      <DropdownDivider divClass="my-1 h-px bg-gray-500 dark:bg-gray-600"/>
      <DropdownItem on:click={makeAllNotificationsAsRead}><div class="text-center">{$LL.NOTIFICATION.MARK_ALL_READ()}</div></DropdownItem>
    {/if}
  </div>
</Dropdown>

<style>
  .wrapper {
    width: min(400px, 100vw);
  }
  .extra-count {
    display: flex;
    font-size: small;
    flex-direction: column;
    align-items: center;
    font-size: small;
  }
  .extra-count:hover {
    cursor: default;
  }
</style>