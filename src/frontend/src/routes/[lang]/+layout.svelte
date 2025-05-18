<script lang="ts">
  import '$lib/base.css';
  import { setLocale } from '$i18n/i18n-svelte';
  import NavBar from '$lib/components/navbar/NavBar.svelte';
  import type { LayoutData } from './$types';
  import Footer from '$lib/components/Footer.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { onMount } from 'svelte';

  export let data: LayoutData;

  setLocale(data.locale);

  let user_info: UserInfo;

  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    if (user_info.is_checked === false) {
      const res = await fetch(`/api/user/me/player`);
      if (res.status != 200) {
        user.update((u) => {
          u.is_checked = true;
          return u;
        });
        return;
      }
      const body = await res.json();
      let me: UserInfo = {
        ...body,
        is_checked: true,
      };
      user.set(me);
    }
  });
</script>

<div class="page-container">
  <header>
    <NavBar />
  </header>
  <div class="container mx-auto">
    <main>
      <slot />
    </main>
  </div>
  <footer>
    <Footer />
  </footer>
</div>

<style>
  .page-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  
  header {
    position: sticky;
    top: 0;
    z-index: 700;
  }
  
  .container {
    flex: 1 0 auto;
    display: flex;
    flex-direction: column;
  }
  
  main {
    flex: 1 0 auto;
    padding-top: 30px;
    padding-bottom: 30px;
    padding-left: 5px;
    padding-right: 5px;
  }
  
  footer {
    flex-shrink: 0;
  }
</style>