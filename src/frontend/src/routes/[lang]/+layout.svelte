<script lang="ts">
  import '$lib/base.css';
  import { setLocale } from '$i18n/i18n-svelte';
  import NavBar from '$lib/components/NavBar.svelte';
  import type { LayoutData } from './$types';
  import Footer from '$lib/components/Footer.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { onMount, setContext } from 'svelte';

  export let data: LayoutData;

  setLocale(data.locale);

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  let permissions: string[] = []; // permissions list passed up from current page
  function addPermission(permission: string) { // function that updates list of all permissions
    permissions.push(permission);
  }
  setContext('page-init', { addPermission });

  onMount(async () => {
    if (user_info.is_checked === false) {
      let permissions_text = permissions.length > 0 ? `?permissions=${permissions.join(',')}` : ""
      const res = await fetch(`/api/user/me/player${permissions_text}`);
      if (res.status != 200) {
        user.update((u) => {
          u.is_checked = true;
          return u;
        });
        return;
      }
      const body = await res.json();
      let me: UserInfo = {
        id: body['id'],
        player_id: body['player_id'],
        player: body['player'],
        permissions: body['permissions'],
        mod_notifications: body['mod_notifications'],
        is_checked: true,
      };
      console.log(me);
      user.set(me);
    }
  });
</script>

<div class="container">
  <header>
    <NavBar />
  </header>

  <main>
    <slot />
  </main>

  <footer>
    <Footer />
  </footer>
</div>

<style>
  /* If the header and main elements are directly placed within the body, the fixed behavior will stop after scrolling one screen's height.
     To prevent this, wrap them in a container. */
  .container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  header {
    position: sticky;
    top: 0;
    z-index: 700;
  }
  main {
    flex: 1 0;
    padding: 30px 50px;
  }
  :global(a) {
    color: white;
    text-decoration: none;
    transition: color .2s ease-out;
  }
  :global(a:hover) {
    color: rgb(0, 162, 255);
    text-decoration: none;
  }
</style>
