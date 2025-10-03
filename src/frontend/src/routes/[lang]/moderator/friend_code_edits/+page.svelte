<script lang="ts">
  import { check_permission, permissions } from '$lib/util/permissions';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import Section from '$lib/components/common/Section.svelte';
  import LL from '$i18n/i18n-svelte';
  import type { FriendCodeEdit, FriendCodeEditList } from '$lib/types/friend-code-edit';
  import PageNavigation from '$lib/components/common/PageNavigation.svelte';
  import { onMount } from 'svelte';
  import Table from '$lib/components/common/Table.svelte';
  import Flag from '$lib/components/common/Flag.svelte';
  import { locale } from '$i18n/i18n-svelte';
  import { page } from '$app/stores';
  import ArrowRight from '$lib/components/common/ArrowRight.svelte';
  import FcTypeBadge from '$lib/components/badges/FCTypeBadge.svelte';
  import NewBadge from '$lib/components/badges/NewBadge.svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let currentPage = 1;
  let totalChanges = 0;
  let totalPages = 0;
  let fc_changes: FriendCodeEdit[] = [];

  async function fetchData() {
    const res = await fetch(`/api/moderator/friendCodeEdits?page=${currentPage}`);
    if (res.status === 200) {
      const body: FriendCodeEditList = await res.json();
      fc_changes = body.change_list;
      totalChanges = body.count;
      totalPages = body.page_count;
    }
  }

  onMount(fetchData);

  const options: Intl.DateTimeFormatOptions = {
    dateStyle: 'short',
    timeStyle: 'short',
  };
</script>

{#if check_permission(user_info, permissions.edit_player)}
  <Section header="Friend Code Changes">
    <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
    {#if totalChanges > 0}
      <Table>
        <col class="player" />
        <col class="date mobile-hide" />
        <col class="fc-type mobile-hide" />
        <col class="fc-info" />
        <col class="handled-by mobile-hide" />
        <thead>
          <tr>
            <th>{$LL.COMMON.PLAYER()}</th>
            <th class="mobile-hide">{$LL.COMMON.DATE()}</th>
            <th class="mobile-hide" />
            <th />
            <th class="mobile-hide">{$LL.MODERATOR.HANDLED_BY()}</th>
          </tr>
        </thead>
        <tbody>
          {#each fc_changes as c, i}
            <tr class="row-{i % 2}">
              <td>
                <a href="/{$page.params.lang}/registry/players/profile?id={c.player.id}">
                  <div class="flex player">
                    <Flag country_code={c.player.country_code} />
                    <div>
                      {c.player.name}
                    </div>
                  </div>
                </a>
              </td>
              <td class="mobile-hide">
                {new Date(c.date * 1000).toLocaleString($locale, options)}
              </td>
              <td class="mobile-hide">
                <FcTypeBadge type={c.fc.type} />
              </td>
              <td>
                <div class="flex fc">
                  {#if c.new_fc}
                    {#if c.old_fc}
                      {c.old_fc}
                      <ArrowRight />
                    {/if}
                    {c.new_fc}
                    {#if c.old_fc === null}
                      <NewBadge />
                    {/if}
                  {:else}
                    {c.fc.fc}
                  {/if}
                  {#if c.is_active !== null}
                    <ArrowRight />
                    {c.is_active ? $LL.FRIEND_CODES.ACTIVE() : $LL.FRIEND_CODES.INACTIVE()}
                  {/if}
                </div>
              </td>
              <td class="mobile-hide">
                {#if c.handled_by}
                  <a href="/{$page.params.lang}/registry/players/profile?id={c.handled_by.id}">
                    <div class="flex player">
                      <Flag country_code={c.handled_by.country_code} />
                      <div>
                        {c.handled_by.name}
                      </div>
                    </div>
                  </a>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </Table>
    {/if}
    <PageNavigation bind:currentPage bind:totalPages refresh_function={fetchData} />
  </Section>
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}

<style>
  .player {
    gap: 10px;
  }
  .fc {
    gap: 5px;
  }
  .flex {
    display: flex;
    flex-direction: row;
    align-items: center;
    flex-wrap: wrap;
  }
  col.player {
    width: 20%;
  }
  col.date {
    width: 20%;
  }
  col.fc-type {
    width: 10%;
  }
  col.fc-info {
    width: 30%;
  }
  col.handled-by {
    width: 20%;
  }
</style>
