<script lang="ts">
    import type { Tournament } from "$lib/types/tournament";
    import Section from "../common/Section.svelte";
    import PostListDisplay from "../posts/PostListDisplay.svelte";
    import type { UserInfo } from "$lib/types/user-info";
    import { user } from "$lib/stores/stores";
    import { check_tournament_permission, tournament_permissions } from "$lib/util/permissions";
    import Button from "../common/buttons/Button.svelte";
    import { page } from "$app/stores";
    import LL from "$i18n/i18n-svelte";

    export let tournament: Tournament;

    let user_info: UserInfo;

    user.subscribe((value) => {
        user_info = value;
    });
</script>

<Section header={$LL.POSTS.TOURNAMENT_ANNOUNCEMENTS()}>
    <div slot="header_content">
        {#if check_tournament_permission(user_info, tournament_permissions.manage_tournament_posts, tournament.id, tournament.series_id)}
            <Button href="/{$page.params.lang}/tournaments/posts/create?tournament_id={tournament.id}">{$LL.POSTS.CREATE_POST()}</Button>
        {/if}
    </div>
    <PostListDisplay tournament_id={tournament.id}/>
</Section>