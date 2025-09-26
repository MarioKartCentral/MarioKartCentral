<script lang="ts">
  import { onMount } from 'svelte';
  import type { AltFlag, AltFlagList } from '$lib/types/alt-flag';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  import Section from '$lib/components/common/Section.svelte';
  import LL from '$i18n/i18n-svelte';
  import AltFlags from '$lib/components/moderator/AltFlags.svelte';
  import { user } from '$lib/stores/stores';
  import type { UserInfo } from '$lib/types/user-info';
  import { check_permission, permissions } from '$lib/util/permissions';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let flags: AltFlag[] = [];

  let currentPage = 1;
  let totalFlags = 0;
  let totalPages = 0;

  let type: string | null = null;
  let exclude_fingerprints = true;

  async function fetchData() {
    let url = `/api/moderator/altFlags?page=${currentPage}`;
    if (type) {
      url += `&type=${type}`;
    }
    if (exclude_fingerprints) {
      url += `&exclude_fingerprints=true`;
    }
    const res = await fetch(url);
    if (res.status === 200) {
      const body: AltFlagList = await res.json();
      flags = body.flags;
      totalFlags = body.count;
      totalPages = body.page_count;
    }
  }

  async function filter() {
    if (type === 'fingerprint_match') {
      exclude_fingerprints = false;
    }
    await fetchData();
  }

  onMount(fetchData);
</script>

{#if user_info.is_checked}
  {#if check_permission(user_info, permissions.view_alt_flags)}
    <Section header={$LL.MODERATOR.ALT_DETECTION.ALT_FLAGS()}>
      {#if totalFlags}
        <div>
          <select bind:value={type} on:change={filter}>
            <option value={null}> All Flags </option>
            <option value="vpn"> VPN </option>
            <option value="ip_match"> IP Matches </option>
            <option value="persistent_cookie_match"> Cookie Matches </option>
            <option value="fingerprint_match"> Fingerprint Matches </option>
          </select>
          <select bind:value={exclude_fingerprints} on:change={fetchData}>
            <option value={true}>Exclude Fingerprints</option>
            <option value={false}>Include Fingerprints</option>
          </select>
        </div>
        <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
        {#key flags}
          <AltFlags {flags} />
        {/key}
        <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
      {/if}
    </Section>
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/if}
