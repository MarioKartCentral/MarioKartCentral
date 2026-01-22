from common.data.command import Command
from common.data.db import DBWrapper
from common.data.models import *
from datetime import datetime, timezone

@dataclass
class RequestVerificationCommand(Command[None]):
    player_id: int | None
    friend_code_ids: list[int]
    verify_player: bool # whether to request verification for the player themselves or just their FCs

    async def handle(self, db_wrapper: DBWrapper):
        if self.player_id is None:
            raise Problem("Must be registered as a player to request verification", status=400)
        async with db_wrapper.connect() as db:
            async with db.execute("SELECT is_verified FROM players WHERE id = ?", (self.player_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise Problem("Player not found", status=404)
                player_is_verified = bool(row[0])

                if self.verify_player and player_is_verified:
                    raise Problem("Player is already verified", status=400)
                
                if not self.verify_player and len(self.friend_code_ids) == 0:
                    raise Problem("At least one friend code must be provided if player is not requesting verification", status=400)
                
            # dictionary to check that we've found every FC in our friend code ID list with 1 query
            found_fcs = {f: False for f in self.friend_code_ids}
            # For now we should only allow players to verify their Switch FCs
            allowed_fc_types = ["switch"]
            async with db.execute(f"""SELECT id, type, fc, is_verified, is_active FROM friend_codes WHERE player_id = ? AND id IN (
                                  {','.join([str(f) for f in self.friend_code_ids])})""", (self.player_id,)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    fc_id, fc_type, fc_fc, fc_is_verified, fc_is_active = row
                    found_fcs[fc_id] = True
                    if bool(fc_is_verified):
                        raise Problem(f"FC with ID {fc_id} ({fc_fc}) is already verified", status=400)
                    if not bool(fc_is_active):
                        raise Problem(f"FC with ID {fc_id} ({fc_fc}) is inactive", status=400)
                    if fc_type not in allowed_fc_types:
                        raise Problem(f"FC with ID {fc_id} ({fc_fc})'s type cannot be verified ({fc_type})", status=400)
                # check to make sure every FC was found from our select query
                for fc_id, found in found_fcs.items():
                    if found is False:
                        raise Problem(f"Friend code with ID {fc_id} could not be found", status=404)
                    
            async with db.execute(f"""SELECT v.id, v.fc_id, f.fc
                                    FROM friend_code_verification_requests v
                                    JOIN friend_codes f ON f.id = v.fc_id
                                    WHERE approval_status = 'pending'
                                    AND v.fc_id IN ({','.join([str(f) for f in self.friend_code_ids])})""") as cursor:
                row = await cursor.fetchone()
                if row:
                    _, fc_id, fc_fc = row
                    raise Problem(f"Friend code with ID {fc_id} ({fc_fc}) already has a pending verification request", status=400)
                    
            now = int(datetime.now(timezone.utc).timestamp())
            if self.verify_player:
                async with db.execute("SELECT id FROM player_verification_requests WHERE player_id = ? AND approval_status = 'pending'", (self.player_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row is not None:
                        raise Problem("Player already has a pending verification request", status=400)
                
                await db.execute("INSERT INTO player_verification_requests(player_id, date, approval_status) VALUES(?, ?, 'pending')", (self.player_id, now))

            await db.executemany("INSERT INTO friend_code_verification_requests(fc_id, date, approval_status) VALUES(?, ?, 'pending')",
                                 [(fc_id, now) for fc_id in self.friend_code_ids])
            await db.commit()

@dataclass
class UpdateVerificationsCommand(Command[None]):
    player_verifications: list[UpdatePlayerVerification]
    fc_verifications: list[UpdateFriendCodeVerification]
    staff_player_id: int

    async def handle(self, db_wrapper: DBWrapper):
        if len(self.player_verifications) == 0 and len(self.fc_verifications) == 0:
            raise Problem("Must specify at least one player/FC verification", status=400)
        
        # Dictionary mapping Verification IDs to a dataclass with two values:
        # update_data: Contains the new approval status we want to change the verification to (so our player_verifications/fc_verifications values)
        # request: The currently existing verification request (set to None at the beginning in case it doesn't exist)
        found_player_verifications: dict[int, CheckPlayerVerificationRequest] = {v.verification_id: CheckPlayerVerificationRequest(v, None) for v in self.player_verifications}
        found_fc_verifications: dict[int, CheckFriendCodeVerificationRequest] = {v.verification_id: CheckFriendCodeVerificationRequest(v, None) for v in self.fc_verifications}
        async with db_wrapper.connect() as db:
            # get the player/FC verifications data from the database in 2 queries
            async with db.execute(f"""SELECT id, player_id, date, approval_status FROM player_verification_requests WHERE id IN (
                                  {','.join([str(v.verification_id) for v in self.player_verifications])})""") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    v_id, p_id, date, approval_status = row
                    v = PlayerVerificationRequestBasic(v_id, p_id, date, approval_status)
                    found_player_verifications[v_id].request = v

            async with db.execute(f"""SELECT id, fc_id, date, approval_status FROM friend_code_verification_requests WHERE id IN (
                                  {','.join([str(v.verification_id) for v in self.fc_verifications])})""") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    v_id, f_id, date, approval_status = row
                    v = FriendCodeVerificationRequestBasic(v_id, f_id, date, approval_status)
                    found_fc_verifications[v_id].request = v

            # checking all player verification requests to make sure everything is valid
            for v_id, v_data in found_player_verifications.items():
                if v_data.request is None:
                    raise Problem(f"Player verification request with ID {v_id} could not be found", status=404)
                # Raise an error if the verification status is the same as it was before
                if v_data.update_data.approval_status == v_data.request.approval_status:
                    raise Problem(f"Player verification request with ID {v_id} already has {v_data.update_data.approval_status} status", status=400)
                # Raise an error if the verification was already approved/denied, as verification requests that have been approved/denied should be immutable
                if v_data.request.approval_status == 'approved':
                    raise Problem(f"Player verification request with ID {v_id} has already been {v_data.request.approval_status} and cannot be changed", status=400)
                # Shouldn't be able to specify a reason when approving a verification request
                if v_data.update_data.approval_status == 'approved' and v_data.update_data.reason:
                    raise Problem(f"Player verification request with ID {v_id} should not have a reason specified when it is being approved", status=400)

            # checking all friend code verification requests to make sure everything is valid  
            for v_id, v_data in found_fc_verifications.items():
                if v_data.request is None:
                    raise Problem(f"Friend Code verification ID {v_id} could not be found", status=404)
                # Raise an error if the verification status is the same as it was before
                if v_data.update_data.approval_status == v_data.request.approval_status:
                    raise Problem(f"Friend Code verification request with ID {v_id} already has {v_data.update_data.approval_status} status", status=400)
                # Raise an error if the verification was already approved/denied, as verification requests that have been approved/denied should be immutable
                if v_data.request.approval_status == 'approved':
                    raise Problem(f"Friend Code verification request with ID {v_id} has already been {v_data.request.approval_status} and cannot be changed", status=400)
                # Shouldn't be able to specify a reason when approving a verification request
                if v_data.update_data.approval_status == 'approved' and v_data.update_data.reason:
                    raise Problem(f"Friend Code verification request with ID {v_id} should not have a reason specified when it is being approved", status=400)
                
            now = int(datetime.now(timezone.utc).timestamp())

            # update player verifications and log approval status changes
            await db.executemany("""INSERT INTO player_verification_request_log(verification_id, date, approval_status, reason, handled_by) VALUES
                                 (?, ?, ?, ?, ?)""", [(v.update_data.verification_id, now, v.update_data.approval_status, v.update_data.reason,
                                                       self.staff_player_id) for v in found_player_verifications.values()])
            await db.executemany("""UPDATE player_verification_requests SET approval_status = ? WHERE id = ?""", 
                                 [(v.update_data.verification_id, v.update_data.approval_status) for v in found_player_verifications.values()])

            # update friend code verifications and log approval status changes
            await db.executemany("""INSERT INTO friend_code_verification_request_log(verification_id, date, approval_status, reason, handled_by) VALUES
                                 (?, ?, ?, ?, ?)""", [(v.update_data.verification_id, now, v.update_data.approval_status, v.update_data.reason,
                                                       self.staff_player_id) for v in found_fc_verifications.values()])
            await db.executemany("""UPDATE friend_code_verification_requests SET approval_status = ? WHERE id = ?""", 
                                 [(v.update_data.verification_id, v.update_data.approval_status) for v in found_fc_verifications.values()])
            await db.commit()

@dataclass
class ListPlayerVerificationsCommand(Command[PlayerVerificationList]):
    filter: PlayerVerificationFilter

    async def handle(self, db_wrapper: DBWrapper):
        async with db_wrapper.connect(db_name="main", attach=["alt_flags"], readonly=True) as db:
            filter = self.filter
            limit = 20
            offset = 0
            if self.filter.page:
                offset = (self.filter.page - 1) * limit

            player_verif_from_where_clause = """FROM player_verification_requests pvr
                JOIN players p ON pvr.player_id = p.id
                WHERE (:from_date IS NULL OR pvr.date >= :from_date)
                AND (:to_date IS NULL OR pvr.date <= :to_date)
                AND (:player_id IS NULL OR pvr.player_id = :player_id)
                AND (:handled_by IS NULL OR pvr.id IN (
                    SELECT pvrl.verification_id 
                    FROM player_verification_request_log pvrl
                    WHERE pvrl.handled_by = :handled_by
                ))"""
            player_verif_query = f"""{player_verif_from_where_clause}
                ORDER BY pvr.id DESC
                LIMIT :limit OFFSET :offset"""
            player_verif_query_params = {"from_date": filter.from_date,
                                  "to_date": filter.to_date,
                                  "player_id": filter.player_id,
                                  "handled_by": filter.handled_by,
                                  "approval_status": filter.approval_status,
                                  "offset": offset,
                                  "limit": limit}
            
            player_verifications: list[PlayerVerificationRequestDetailed] = []
            # player_id_verif_dict is used to get verifications by player ID in the
            # friend code and alt flag queries in O(1) time
            player_id_verif_dict: dict[int, list[PlayerVerificationRequestDetailed]] = {}
            async with db.execute(f"""SELECT pvr.id, pvr.date, pvr.approval_status,
                                    p.id, p.name, p.country_code, p.is_banned, p.is_verified
                                  {player_verif_query}""", player_verif_query_params) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    v_id, v_date, v_approval, p_id, p_name, p_country, p_banned, p_verified = row
                    player = PlayerBasic(p_id, p_name, p_country, bool(p_banned), bool(p_verified))
                    verification = PlayerVerificationRequestDetailed(v_id, v_date, v_approval, player, [], [])
                    player_verifications.append(verification)
                    if p_id not in player_id_verif_dict:
                        player_id_verif_dict[p_id] = []
                    player_id_verif_dict[p_id].append(verification)

            # here we get pending FC verifications for any players that appear in the results of our earlier query.
            # this is used on the frontend so staff can easily approve both player/FC verifications on the same page.
            if filter.get_pending_fc_verifications:
                fc_query = f"""SELECT fvr.id, fvr.date, fvr.approval_status, f.id, f.player_id, f.type,
                    f.fc, f.is_verified, f.is_primary, f.is_active, f.description, f.creation_date
                    FROM friend_code_verification_requests fvr
                    JOIN friend_codes f ON fvr.fc_id = f.id
                    WHERE approval_status = 'pending'
                    AND f.player_id IN (SELECT pvr.player_id {player_verif_query})"""
                async with db.execute(fc_query, player_verif_query_params) as cursor:
                    rows = await cursor.fetchall()
                    for row in rows:
                        (v_id, v_date, v_approval, f_id, f_player_id, f_type, f_fc, f_verified, f_primary,
                        f_active, f_description, f_date) = row
                        fc = FriendCode(f_id, f_fc, f_type, f_player_id, bool(f_verified), bool(f_primary),
                                        f_date, f_description, bool(f_active))
                        # get all verifications linked to player with same player ID as the FC,
                        # and add the pending FC verifications to it
                        player_verifs = player_id_verif_dict[f_player_id]
                        verification = FriendCodeVerificationRequest(v_id, v_date, v_approval, player_verifs[0].player, fc)
                        for v in player_verifs:
                            v.fc_verifications.append(verification)
        
            # next we count alt flags for every player in our verifications
            alt_flag_query = f"""SELECT u.player_id, COUNT(af.id)
                FROM alt_flags.alt_flags af
                JOIN alt_flags.user_alt_flags uaf ON uaf.flag_id = af.id
                JOIN users u ON u.id = uaf.user_id
                WHERE u.player_id IN (
                    SELECT p.id {player_verif_query}
                )
                GROUP BY u.player_id"""
            async with db.execute(alt_flag_query, player_verif_query_params) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    player_id, alt_flag_count = row
                    player_verifs = player_id_verif_dict[player_id]
                    # add the player alt flag count to all verifications linked to that player ID
                    for v in player_verifs:
                        v.alt_flag_count = alt_flag_count

            # get the total count and page count for verifications with these parameters
            count_query = f"""SELECT COUNT(*) {player_verif_from_where_clause}"""
            async with db.execute(count_query, player_verif_query_params) as cursor:
                row = await cursor.fetchone()
                assert row is not None
                count = row[0]
                page_count = (count + limit - 1) // limit

            return PlayerVerificationList(player_verifications, count, page_count)