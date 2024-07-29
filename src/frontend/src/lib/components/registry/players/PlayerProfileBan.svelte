<script lang="ts">
  import type { BanInfoDetailed } from '$lib/types/ban-info';

  export let ban_info: BanInfoDetailed;
</script>

<div class="container">
  This player is <b>banned</b> and may not participate in MKCentral competitions.
  <br />
  <b>Reason: </b>
  {ban_info.reason}
</div>

<style>
  div.container {
    width: 50%;
    margin: 20px auto 20px auto;
    background-color: darkred;
    color: #de858f;
    padding: 5px;
  }
</style>
