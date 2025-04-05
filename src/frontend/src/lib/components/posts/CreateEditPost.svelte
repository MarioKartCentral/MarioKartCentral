<script lang="ts">
    import MarkdownTextArea from "../common/MarkdownTextArea.svelte";
    import Section from "../common/Section.svelte";
    import Button from "../common/buttons/Button.svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import type { Post } from "$lib/types/posts";
    import LL from "$i18n/i18n-svelte";

    export let id: number | null = null;
    export let series_id: number | null = null;
    export let tournament_id: number | null = null;

    let title = "";
    let is_public = true;
    let content = "";

    onMount(async() => {
        if(!id) return;
        let path = tournament_id ? `tournaments/${tournament_id}/` : series_id ? `tournaments/series/${series_id}/`: ``;
        let url = `/api/${path}posts/${id}`;
        const res = await fetch(url);
        if(res.status === 200) {
            const body: Post = await res.json();
            title = body.title;
            is_public = body.is_public;
            content = body.content;
        }
    });

    async function createEditPost(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
        const formData = new FormData(event.currentTarget);
        const payload = {
            title: formData.get("title"),
            is_public: formData.get("is_public") === "true",
            content: formData.get("content"),
        };
        let suffix = `${id ? `${id}/edit` : "create"}`;
        let path = tournament_id ? `tournaments/${tournament_id}/` : series_id ? `tournaments/series/${series_id}/`: ``;
        const endpoint = `/api/${path}posts/${suffix}`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.status < 300) {
            let new_id = result["id"];
            let page_path = tournament_id ? `tournaments/` : series_id ? `tournaments/series/` : '';
            let page_suffix = tournament_id ? `&tournament_id=${tournament_id}` : series_id ? `&series_id=${series_id}` : '';
            goto(`/${$page.params.lang}/${page_path}posts/view?id=${new_id}${page_suffix}`);
        }
        else {
            alert(`${$LL.POSTS.CREATE_EDIT_POST_FAILED()}: ${result['title']}`);
        }
    }
</script>

<Section header={id ? $LL.POSTS.EDIT_POST() : $LL.POSTS.CREATE_POST()}>
    <form on:submit|preventDefault={createEditPost}>
        <div class="option">
            <label for="title">{$LL.POSTS.POST_TITLE()}</label>
            <div>
                <input name="title" bind:value={title} required/>
            </div>
        </div>
        <div class="option">
            <label for="is_public">{$LL.POSTS.VISIBILITY()}</label>
            <div>
                <select name="is_public" bind:value={is_public} required>
                    <option value={true}>
                        {$LL.POSTS.PUBLIC()}
                    </option>
                    <option value={false}>
                        {$LL.POSTS.HIDDEN()}
                    </option>
                </select>
            </div>
        </div>
        <div class="option">
            <label for="content">{$LL.POSTS.CONTENT()}</label>
            <MarkdownTextArea name="content" bind:value={content}/>
        </div>
        <Button type="submit">{$LL.COMMON.SUBMIT()}</Button>
    </form>
</Section>

<style>
    div.option {
        margin-bottom: 10px;
    }
</style>