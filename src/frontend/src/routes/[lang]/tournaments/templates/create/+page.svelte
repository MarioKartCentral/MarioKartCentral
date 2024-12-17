<script lang="ts">
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_permission, series_permissions } from '$lib/util/permissions';
  import LL from '$i18n/i18n-svelte';

  let template_id: number | null;

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('template_id');
    template_id = param_temp_id ? Number(param_temp_id) : null;
  });
</script>

{#if check_permission(user_info, series_permissions.create_tournament_template)}
  {#key template_id}
    <CreateEditTemplateForm {template_id} />
  {/key}
{:else}
  {$LL.COMMON.NO_PERMISSION()}
{/if}
