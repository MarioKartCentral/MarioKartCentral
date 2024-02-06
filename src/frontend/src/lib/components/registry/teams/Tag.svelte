<script lang="ts">
    import type { Team } from '$lib/types/team';
    export let team: Team;
  </script>
  
  <span class={'tag_badge team_badge_' + (team.color + 1)}>
    {team.tag}
  </span>
  
  <style>
    .tag_badge {
      background: rgba(255, 255, 255, 0.2);
      color: white;
      border-radius: 6px;
      display: inline-block;
      text-align: center;
      width: 40px;
      vertical-align: middle;
      overflow: hidden;
      height: 30px;
      line-height: 30px;
      position: relative;
         
    }
  
    span.team_badge_1 {
      background-color: #ef5350;
    }
  
    span.team_badge_2 {
      background-color: #ffa726;
    }
  
    span.team_badge_3 {
      background-color: #d4e157;
    }
  
    span.team_badge_4 {
      background-color: #66bb6a;
    }
  
    span.team_badge_5 {
      background-color: #26a69a;
    }
  
    span.team_badge_6 {
      background-color: #29b6f6;
    }
  
    span.team_badge_7 {
      background-color: #5c6bc0;
    }
  
    span.team_badge_8 {
      background-color: #7e57c2;
    }
  
    span.team_badge_9 {
      background-color: #ec407a;
    }
  
    span.team_badge_10 {
      background-color: #888888;
    }
  
    span.team_badge_11 {
      background-color: #c62828;
    }
  
    span.team_badge_12 {
      background-color: #ef6c00;
    }
  
    span.team_badge_13 {
      background-color: #9e9d24;
    }
  
    span.team_badge_14 {
      background-color: #2e7d32;
    }
  
    span.team_badge_15 {
      background-color: #00897b;
    }
  
    span.team_badge_16 {
      background-color: #0277bd;
    }
  
    span.team_badge_17 {
      background-color: #283593;
    }
  
    span.team_badge_18 {
      background-color: #4527a0;
    }
  
    span.team_badge_19 {
      background-color: #ad1457;
    }
  
    span.team_badge_20 {
      background-color: #444444;
    }
  
    span.team_badge_21 {
      background-color: #d44a48;
    }
  
    span.team_badge_22 {
      background-color: #e69422;
    }
  
    span.team_badge_23 {
      background-color: #bdc74e;
    }
  
    span.team_badge_24 {
      background-color: #4a874c;
    }
  
    span.team_badge_25 {
      background-color: #208c81;
    }
  
    span.team_badge_26 {
      background-color: #25a5db;
    }
  
    span.team_badge_27 {
      background-color: #505ca6;
    }
  
    span.team_badge_28 {
      background-color: #6c4ca8;
    }
  
    span.team_badge_29 {
      background-color: #d13b6f;
    }
  
    span.team_badge_30 {
      background-color: #545454;
    }
  
    span.team_badge_31 {
      background-color: #ab2424;
    }
  
    span.team_badge_32 {
      background-color: #d45f00;
    }
  
    span.team_badge_33 {
      background-color: #82801e;
    }
  
    span.team_badge_34 {
      background-color: #205723;
    }
  
    span.team_badge_35 {
      background-color: #006e61;
    }
  
    span.team_badge_36 {
      background-color: #0369a3;
    }
  
    span.team_badge_37 {
      background-color: #222d78;
    }
  
    span.team_badge_38 {
      background-color: #382185;
    }
  
    span.team_badge_39 {
      background-color: #91114b;
    }
  
    span.team_badge_40 {
      background-color: #000000;
    }
  </style>
  