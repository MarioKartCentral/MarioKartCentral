from dataclasses import dataclass

@dataclass
class RequestVerificationRequestData:
    verify_player: bool
    friend_code_ids: list[int]