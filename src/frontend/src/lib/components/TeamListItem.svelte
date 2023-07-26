<script lang="ts">
    import type { Team } from "$lib/types/team";

    export let team: Team;
</script>

<div>
    <tr>
        <td>
            {team.tag}
        </td>
        <td>
            {team.name}
        </td>
    </tr>
    
</div>

<style>
    td {
        padding: 10px;
        text-align: center;
    }
</style>