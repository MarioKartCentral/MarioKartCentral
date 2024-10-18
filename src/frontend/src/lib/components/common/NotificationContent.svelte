<script lang="ts">
  import { InfoCircleSolid } from 'flowbite-svelte-icons';
  import Caution from '../icons/Caution.svelte';
  import LL from '$i18n/i18n-svelte';
  import { locale } from "$i18n/i18n-svelte";

  export let type: number;
  export let content_id: number;
  export let content_args: string[];
  export let created_date: number;
  export let is_read: boolean;

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };

  function formatNotificationContent(contentId: number, contentArgs: (string | null)[]) {
    const contentLookup: { [key: string]: () => string } = $LL.NOTIFICATION_CONTENT; // this makes the linter happy
    let content = contentLookup[contentId.toString()]();

    // special cases for when squad name is null
    if (contentId === 2 && !contentArgs[0])
      content = contentLookup['2b']();

    for (let word of content.split(" ")) {
      if (!word.startsWith('$'))
        continue;
      const idx = parseInt(word.substring(1));
      let arg = contentArgs[idx] || "_";
      if (arg.startsWith('DATE-')) {
        const timestamp = parseInt(arg.replace('DATE-', '')) * 1000;
        arg = new Date(timestamp).toLocaleString($locale, options);
      }
      content = content.replace(`$${idx}`, `${arg}`);
    }

    return content;
  }
</script>

<div class="container">
  <div class="icon">
    {#if type === 1}
      <Caution color="#F1B21C"/>
    {:else if type === 2}
      <Caution color="red"/>
    {:else if type === 3}
      <InfoCircleSolid color="#3FD14D"/>
    {:else}
      <InfoCircleSolid color="#4DBBFF"/>
    {/if}
  </div>
  <div class="unread-dot {!is_read ? 'unread-dot-show' : ''}"></div>
  <div class="content-wrapper">
    <div class="date">
      {new Date(created_date * 1000).toLocaleString()}
    </div>
    <p> 
      {formatNotificationContent(content_id, content_args)}
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