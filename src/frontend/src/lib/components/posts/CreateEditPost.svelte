<script lang="ts">
  import MarkdownTextArea from '../common/MarkdownTextArea.svelte';
  import Section from '../common/Section.svelte';
  import Button from '../common/buttons/Button.svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import type { Post } from '$lib/types/posts';
  import LL from '$i18n/i18n-svelte';

  export let postId: number | null = null;
  export let seriesId: number | null = null;
  export let tournamentId: number | null = null;

  const isEdit = Boolean(postId);

  let title = '';
  let isPublic = true;
  let content = '';
  let working = false;

  $: baseApiPath = (() => {
    if (tournamentId) return `/api/tournaments/${tournamentId}/posts`;
    if (seriesId) return `/api/tournaments/series/${seriesId}/posts`;
    return '/api/posts';
  })();

  const getPagePath = (postId: number, tournamentId: number | null, seriesId: number | null): string => {
    const searchParams = new URLSearchParams({ id: postId.toString() });
    let path = `${$page.params.lang}`;

    if (tournamentId) {
      path += '/tournaments';
      searchParams.append('tournament_id', tournamentId.toString());
    } else if (seriesId) {
      path += '/tournaments/series';
      searchParams.append('series_id', seriesId.toString());
    }
    return `/${path}/posts/view?${searchParams.toString()}`;
  };

  onMount(async () => {
    if (!isEdit) return;
    const response = await fetch(baseApiPath + `/${postId}`);
    if (response.ok) {
      ({ is_public: isPublic, title, content } = (await response.json()) as Post);
    }
  });

  async function createEditPost() {
    working = true;
    const payload = {
      title,
      is_public: isPublic,
      content,
    };
    let endpoint = baseApiPath;
    if (isEdit) endpoint += `/${postId}`;
    const response = await fetch(endpoint, {
      method: isEdit ? 'PATCH' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    working = false;
    const result = await response.json();
    if (response.ok) {
      postId = result['id'];
      const path = getPagePath(postId as number, tournamentId, seriesId);
      goto(path);
    } else {
      alert(`${$LL.POSTS.CREATE_EDIT_POST_FAILED()}: ${result['title']}`);
    }
  }
</script>

<Section header={isEdit ? $LL.POSTS.EDIT_POST() : $LL.POSTS.CREATE_POST()}>
  <form on:submit|preventDefault={createEditPost}>
    <div class="option">
      <label for="title">{$LL.POSTS.POST_TITLE()}</label>
      <div>
        <input name="title" bind:value={title} required />
      </div>
    </div>
    <div class="option">
      <label for="is_public">{$LL.POSTS.VISIBILITY()}</label>
      <div>
        <select name="is_public" bind:value={isPublic} required>
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
      <MarkdownTextArea name="content" bind:value={content} />
    </div>
    <Button {working} type="submit">{$LL.COMMON.SUBMIT()}</Button>
  </form>
</Section>

<style>
  div.option {
    margin-bottom: 10px;
  }
</style>
