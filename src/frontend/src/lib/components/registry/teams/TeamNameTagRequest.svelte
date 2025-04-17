<script lang="ts">
    import type { Team } from "$lib/types/team";
    import Button from "$lib/components/common/buttons/Button.svelte";
    import LL from "$i18n/i18n-svelte";
    import { onMount } from "svelte";
    import type { TeamEditRequest } from '$lib/types/team-edit-request';

    export let team: Team;

    let requests: TeamEditRequest[] = [];
    let pending_requests: TeamEditRequest[] = [];

    let days_until_change = 0;
    let days_between_changes = 90;
    let working = false;

    onMount(async() => {
        const res = await fetch(`/api/registry/teams/${team.id}/editRequests`);
        if (res.status != 200) {
            return;
        }
        const body: TeamEditRequest[] = await res.json();
        requests = body;
        pending_requests = requests.filter((r) => r.approval_status === "pending");
        // using the most recent name change request, see if it's been 90 days since then and update days_until_change
        if(requests.length) {
            let last_date = new Date(requests[requests.length-1].date * 1000);
            last_date.setDate(last_date.getDate() + days_between_changes);
            let now = new Date();
            days_until_change = Math.round((last_date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        }
    });

    async function editNameTag(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        working = true;
      const data = new FormData(event.currentTarget);
      const payload = {
        team_id: team.id,
        name: data.get('name')?.toString(),
        tag: data.get('tag')?.toString(),
      };
      console.log(payload);
      const endpoint = '/api/registry/teams/requestChange';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      working = false;
      const result = await response.json();
      if (response.status < 300) {
        window.location.reload();
        alert($LL.TEAMS.EDIT.NAME_TAG_CHANGE_SUCCESS());
      } else {
        alert(`${$LL.TEAMS.EDIT.NAME_TAG_CHANGE_FAILURE()}: ${result['title']}`);
      }
    }
</script>

<form method="post" on:submit|preventDefault={editNameTag}>
    {#if days_until_change > 0}
        <div>
            {$LL.TEAMS.EDIT.REQUEST_CHANGE_IN({days: days_until_change})}
        </div>
    {/if}
    {#if pending_requests.length}
        {#each pending_requests as r}
            <div>
                {$LL.TEAMS.EDIT.NAME_TAG_CHANGE_PENDING()}
            </div>
            <div>
                <label for="name">{$LL.TEAMS.EDIT.TEAM_NAME()}</label>
                <input name="name" type="text" value={r.new_name} required disabled/>
            </div>
            <div>
                <label for="tag">{$LL.TEAMS.EDIT.TEAM_TAG()}</label>
                <input name="tag" type="text" value={r.new_tag} required disabled/>
            </div>
        {/each}
    {:else}
        <div>
            <label for="name">{$LL.TEAMS.EDIT.TEAM_NAME()}</label>
            <input name="name" type="text" value={team.name} required disabled={days_until_change > 0} maxlength=32/>
        </div>
        <div>
            <label for="tag">{$LL.TEAMS.EDIT.TEAM_TAG()}</label>
            <input name="tag" type="text" value={team.tag} required disabled={days_until_change > 0} maxlength=5/>
        </div>
        <div class="submit">
            <Button type="submit" disabled={days_until_change > 0} {working}>{$LL.TEAMS.EDIT.REQUEST_NAME_TAG_CHANGE()}</Button>
        </div>
    {/if}
</form>

<style>
    label {
        display: inline-block;
        width: 100px;
    }
    .submit {
        margin-top: 10px;
    }
</style>