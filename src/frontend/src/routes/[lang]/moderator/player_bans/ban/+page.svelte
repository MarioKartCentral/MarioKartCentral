<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import type { PlayerInfo } from '$lib/types/player-info';
    import PlayerBanDetailsForm from '$lib/components/moderator/PlayerBanDetailsForm.svelte';
    import PlayerSearch from '$lib/components/common/PlayerSearch.svelte';
    import Section from '$lib/components/common/Section.svelte';

    let player: PlayerInfo | null = null;

    onMount(async () => {
      let paramId = $page.url.searchParams.get('id')
      if (paramId) {
        const res = await fetch(`/api/registry/players/${paramId}`)
        if (res.status != 200)
            return
        player = await res.json()
      }
    });

    async function banPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if (!player)
            return alert('You need to select a player')
        
        const data = new FormData(event.currentTarget)
        let expirationDate = 0
        if (data.get('days')) {
            expirationDate = Math.floor((Date.now() + 86400000*data.get('days')) / 1000)
        }

        const payload = {
            is_indefinite: data.get('duration') === 'indefinite',
            expiration_date: expirationDate,
            reason: data.get('custom_reason') || data.get('reason')
        };

        const endpoint = `/api/registry/players/${player.id}/ban`
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json()

        if (response.status < 300) {
            alert(`Successfully banned ${player.name} (Player ID: ${player.id})`)
            goto('/moderator/player_bans')
        } else {
            const detail = result.detail ? `, ${result.detail}` : ''
            alert(`${result.title}${detail}`)
        }
    }
</script>

<div>
    <Section header='Select Player'>
        <PlayerSearch bind:player={player}/>
    </Section>
    <PlayerBanDetailsForm handleSubmit={banPlayer}/>
</div>