<script lang="ts">
  import DOMPurify from 'dompurify';
  import { InfoCircleSolid } from 'flowbite-svelte-icons';
  import Caution from '../icons/Caution.svelte';
  import LL from '$i18n/i18n-svelte';
  import { locale } from '$i18n/i18n-svelte';

  export let type: number;
  export let content_id: number;
  export let content_args: { [key: string]: string };
  export let created_date: number;
  export let is_read: boolean;

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'medium',
    timeStyle: 'short',
  };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const notificationContent: any = $LL.NOTIFICATION_CONTENT;
</script>

<div class="container">
  <div class="icon">
    {#if type === 1}
      <Caution color="#F1B21C" />
    {:else if type === 2}
      <Caution color="red" />
    {:else if type === 3}
      <InfoCircleSolid color="#3FD14D" />
    {:else}
      <InfoCircleSolid color="#4DBBFF" />
    {/if}
  </div>
  <div class="unread-dot {!is_read ? 'unread-dot-show' : ''}"></div>
  <div class="content-wrapper">
    <div class="date">
      {new Date(created_date * 1000).toLocaleString($locale, options)}
    </div>
    <p>
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html DOMPurify.sanitize(notificationContent[content_id.toString()](content_args), { ALLOWED_TAGS: ['strong'] })}
    </p>
  </div>
</div>

<style>
  .container {
    display: flex;
  }
  .date {
    font-size: smaller;
    text-align: left;
  }
  .unread-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    position: relative;
    left: -7px;
    top: 7px;
  }
  .unread-dot-show {
    background-color: rgb(39, 183, 255);
  }
  .icon {
    margin-right: 30px;
    display: flex;
    align-items: center;
  }
  p {
    padding-top: 5px;
    text-align: left;
    overflow-wrap: break-word;
  }
  .content-wrapper {
    width: calc(100% - 60px);
  }
</style>
