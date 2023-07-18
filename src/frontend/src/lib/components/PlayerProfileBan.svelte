<script lang="ts">
    import type { BanInfo } from "$lib/types/ban-info";

    export let ban_info: BanInfo;
</script>

<div class="container">
    <div class="inner">
        This player is <b>banned</b> and may not participate in MKCentral competitions.
        <br>
        <b>Reason: </b> {ban_info.reason}
    </div>
    
</div>

<style>
    div.container {
        background-color: darkred;
        color: #de858f;
        margin: 10px 0;
    }
    div.inner {
        margin: 5px;
    }
</style>