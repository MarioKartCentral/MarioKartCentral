<script lang="ts">
    import { page } from '$app/stores';
    import type { TeamRoster } from '$lib/types/team-roster';
    import Table from '$lib/components/common/Table.svelte';
    import Section from '$lib/components/common/Section.svelte';
    import { locale } from '$i18n/i18n-svelte';
    import Dialog from "$lib/components/common/Dialog.svelte";
    import LinkButton from '$lib/components/common/LinkButton.svelte';
  
    export let roster: TeamRoster;
    let kick_dialog: Dialog;
    let invite_player_id: number = 0;
  
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour12: true,
    };

    async function invitePlayer(player_id: number) {
        const payload = {
            team_id: roster.team_id,
            roster_id: roster.id,
            player_id: player_id
        }
        const endpoint = '/api/registry/teams/invitePlayer';
        const response = await fetch(endpoint, {
        method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            window.location.reload();
        } else {
            alert(`Player invite failed: ${result['title']}`);
        }
    }

    async function retractInvite(player_id: number) {
        const payload = {
            team_id: roster.team_id,
            roster_id: roster.id,
            player_id: player_id
        }
        console.log(payload);
        const endpoint = '/api/registry/teams/deleteInvite';
        const response = await fetch(endpoint, {
        method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            //goto(`/${$page.params.lang}/registry/teams/manage_rosters?id=${roster.team_id}`);
            window.location.reload();
        } else {
            alert(`Deleting invite failed: ${result['title']}`);
        }
    }
  </script>

  <Section header="Team Page">
    <div slot="header_content">
        <LinkButton href="/{$page.params.lang}/registry/teams/profile?id={roster.id}">
            Back to Team
        </LinkButton>
    </div>
  </Section>
  
  <Section header="{roster.game} {roster.name}">
    {roster.players.length} player{roster.players.length !== 1 ? 's' : ''}
    {#if roster.players.length}
        <Table>
        <col class="country" />
        <col class="name" />
        <col class="fc" />
        <col class="join_date" />
        <col class="manage_player"/>
        <thead>
            <tr>
            <th />
            <th>Name</th>
            <th>Friend Code</th>
            <th>Join Date</th>
            <th/>
            </tr>
        </thead>
        <tbody>
            {#each roster.players as player}
            <tr>
                <td>{player.country_code}</td>
                <td>{player.name}</td>
                <td>{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
                <td>{new Date(player.join_date * 1000).toLocaleString($locale, options)}</td>
                <td>
                    <button>Kick</button>
                </td>
            </tr>
            {/each}
        </tbody>
        </Table>
    {/if}
    <br/><br/>
    <h3>Invitations</h3>
    {#if roster.invites.length}
        <Table>
        <col class="country" />
        <col class="name" />
        <col class="fc" />
        <col class="join_date" />
        <col class="manage_player"/>
        <thead>
            <tr>
            <th />
            <th>Name</th>
            <th>Friend Code</th>
            <th>Join Date</th>
            <th/>
            </tr>
        </thead>
        <tbody>
            {#each roster.invites as player}
            <tr>
                <td>{player.country_code}</td>
                <td>{player.name}</td>
                <td>{player.friend_codes.filter((fc) => fc.game === roster.game)[0].fc}</td>
                <td>{new Date(player.invite_date * 1000).toLocaleString($locale, options)}</td>
                <td>
                    <button on:click={() => retractInvite(player.player_id)}>Retract Invite</button>
                </td>
            </tr>
            {/each}
        </tbody>
        </Table>
    {/if}
    <br/>
    <b>Invite Player</b>
    <br/>
    <input type="number" placeholder="Player ID" min="1" bind:value={invite_player_id}/>
    {#if invite_player_id}
        <button on:click={() => invitePlayer(invite_player_id)}>Invite Player</button>
    {/if}
</Section>

<Dialog bind:this={kick_dialog}>
</Dialog>