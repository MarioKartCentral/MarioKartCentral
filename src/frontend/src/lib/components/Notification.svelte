<script lang="ts">
  import type { Notification } from '$lib/types/notification';
  import { onMount } from 'svelte';
  import { have_unread_notification } from '$lib/stores/stores';
  import DropdownMenu from './DropdownMenu.svelte';
  import Dropdown from './common/Dropdown.svelte';
  import DropdownItem from './common/DropdownItem.svelte';
  import LL from '$i18n/i18n-svelte';

  let dropdown: DropdownMenu;
  export function toggleNotificationMenu() {
    dropdown.toggleDropdown();
  }

  let notifications: Notification[] = [];
  $: {
    have_unread_notification.set(notifications.filter((n) => !n.is_read).length);
  }

  onMount(async () => {
    const res = await fetch('/api/notifications/list?is_read=0');
    if (res.status !== 200) {
      return;
    }
    const body = (await res.json()) as Notification[];
    notifications = body;
  });

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
      // change target notification.is_read to true
      // TODO: ...or delete depending on requirements.
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
      // change all notification.is_read to true
      // TODO: ...or delete depending on requirements.
      notifications = notifications.map((n) => ({
        ...n,
        is_read: true,
      }));
    }
  }
</script>

<!-- <DropdownMenu bind:this={dropdown}>
  <ul>
    {#each notifications as { id, content, created_date, is_read, type }}
      <li>
        <div class="notification-item">
          <span>{id}: </span>
          <span>{content}</span>
          <span>{new Date(created_date * 1000).toLocaleString()}</span>
          <span>{$LL.NAVBAR.TYPE()}: {type}</span>
          <button on:click={async () => await makeNotificationAsRead(id)}>☑</button>
          <span>{$LL.NAVBAR.IS_READ()}: {is_read}</span>
        </div>
      </li>
    {/each}
    <li>
      <div class="notification-item">
        <button on:click={makeAllNotificationsAsRead}>{$LL.NAVBAR.MARK_ALL_READ()}</button>
      </div>
    </li>
  </ul>
</DropdownMenu> -->
<Dropdown>
  {#each notifications as { id, content, created_date, is_read, type }}
    <DropdownItem>
      <span>{id}: </span>
      <span>{content}</span>
      <span>{new Date(created_date * 1000).toLocaleString()}</span>
      <span>{$LL.NAVBAR.TYPE()}: {type}</span>
      <button on:click={async () => await makeNotificationAsRead(id)}>☑</button>
      <span>{$LL.NAVBAR.IS_READ()}: {is_read}</span>
    </DropdownItem>
  {/each}
  <DropdownItem>
    <button on:click={makeAllNotificationsAsRead}>{$LL.NAVBAR.MARK_ALL_READ()}</button>
  </DropdownItem>
</Dropdown>

<style>
  ul {
    list-style: none;
    padding: 0;
  }

  .notification-item {
    border-bottom: 1px solid #f2f2f2;
    padding: 10px;
  }
</style>
