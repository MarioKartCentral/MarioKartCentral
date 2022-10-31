<script lang="ts">
  import '$lib/base.css'
  import { setLocale } from '$i18n/i18n-svelte';
  import NavBar from '$lib/components/NavBar.svelte';
  import type { LayoutData } from './$types';
    import Footer from '$lib/components/Footer.svelte';

  export let data : LayoutData;
  
  setLocale(data.locale);
</script>

<header>
  <NavBar/>
</header>

<main>
  <slot/>
</main>

<footer>
  <Footer/>
</footer>

<style>
  main {
    flex: 1 0;
    padding: 30px 50px;
  }
</style>