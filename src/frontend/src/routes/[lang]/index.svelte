<script lang="ts">
  import LL from '$i18n/i18n-svelte';
</script>

<h1>{@html $LL.WELCOME()}</h1>
<p>{@html $LL.SUMMARY()}</p>
<p>Language: {$LL.LANGUAGE()}</p>
