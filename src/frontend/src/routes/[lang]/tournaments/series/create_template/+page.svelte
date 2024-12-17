<script lang="ts">
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_series_permission, series_permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let template_id: number | null;
  let series_id: number | null;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('template_id');
    template_id = param_temp_id ? Number(param_temp_id) : null;

    let param_series_id = $page.url.searchParams.get('series_id');
    series_id = param_series_id ? Number(param_series_id) : null;
  });
</script>

{#key series_id}
  {#if check_series_permission(user_info, series_permissions.create_tournament_template, series_id)}
    <CreateEditTemplateForm {template_id} {series_id} series_restrict={true} />
  {:else}
    {$LL.COMMON.NO_PERMISSION()}
  {/if}
{/key}