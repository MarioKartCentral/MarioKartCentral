<script lang="ts">
    import type { PlayerInfo } from '$lib/types/player-info';
    import PlayerBanDetailsForm from '$lib/components/moderator/BanDetailsForm.svelte';

    export let player: PlayerInfo | null = null;

    async function banPlayer(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        if (!player)
            return alert('A player is not selected')
        
        const data = new FormData(event.currentTarget)
        let expirationDate = 0
        let days = Number(data.get('days'))
        if (days) {
            expirationDate = Math.floor((Date.now() + 86400000*days) / 1000)
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
            window.location.reload()
        } else {
            const detail = result.detail ? `, ${result.detail}` : ''
            alert(`${result.title}${detail}`)
        }
    }
</script>

<PlayerBanDetailsForm handleSubmit={banPlayer}/>