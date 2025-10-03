<script lang="ts">
  import Badge from './Badge.svelte';
  import type { Role } from '$lib/types/role';

  export let role: Role;
  export let style = '';

  const role_classes: { [key: string]: string } = {
    'Super Administrator': 'super_administrator',
    Administrator: 'administrator',
    'Site Moderator': 'site_moderator',
    'Support Staff': 'support_staff',
    'Site Supporter': 'site_supporter',
    'Event Admin': 'event_admin',
    'Event Mod': 'event_mod',
    Banned: 'banned',
    'Team Leader Banned': 'team_leader_banned',
  };

  function get_role_class() {
    if (Object.keys(role_classes).includes(role.name)) {
      return role_classes[role.name];
    } else {
      return '';
    }
  }
</script>

<Badge badgeClass="role_{get_role_class()}_badge wide" {style}>{role.name}</Badge>
