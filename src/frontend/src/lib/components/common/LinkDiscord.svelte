<script lang="ts">
    import { user } from '$lib/stores/stores';
    import type { UserInfo } from '$lib/types/user-info';
    import Button from '$lib/components/common/buttons/Button.svelte';

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });

    async function linkDiscord() {
        let url = `/api/user/link_discord?page_url=${encodeURIComponent(window.location.href)}`;
        window.location.replace(url);
    }
</script>

<Button on:click={linkDiscord}>Link Discord Account</Button>