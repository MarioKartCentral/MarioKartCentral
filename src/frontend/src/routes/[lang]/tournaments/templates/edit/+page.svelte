<script lang="ts">
  import { page } from '$app/stores';
  import CreateEditTemplateForm from '$lib/components/tournaments/templates/CreateEditTemplateForm.svelte';
  import { onMount } from 'svelte';
  import type { UserInfo } from '$lib/types/user-info';
  import { user } from '$lib/stores/stores';
  import { check_permission, series_permissions } from '$lib/util/permissions';

  let user_info: UserInfo;
  user.subscribe((value) => {
    user_info = value;
  });

  let template_id: number;

  onMount(async () => {
    let param_temp_id = $page.url.searchParams.get('id');
    template_id = Number(param_temp_id);
  });
</script>

{#if template_id}
  <CreateEditTemplateForm {template_id} is_edit={true}
  series_restrict={!check_permission(user_info, series_permissions.edit_tournament_template)} />
{/if}
