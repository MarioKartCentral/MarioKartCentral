
from dataclasses import dataclass

import bcrypt
import msgspec
from common.data import s3
from common.data.models.common import Problem
from common.data.models.mkcv1 import *
from common.data.commands import Command

@dataclass
class ImportMKCV1DataCommand(Command[None]):
    data: MKCV1Data

    async def handle(self, db_wrapper, s3_wrapper):
        # These json files should not be public as they contain secrets, so store them with a private acl
        serialised_mkc: bytes = msgspec.json.encode(self.data.mkc)
        await s3_wrapper.put_object(s3.MKCV1_BUCKET, "mkc.json", serialised_mkc, acl="private")
        serialised_xf: bytes = msgspec.json.encode(self.data.xf)
        await s3_wrapper.put_object(s3.MKCV1_BUCKET, "xf.json", serialised_xf, acl="private")

@dataclass
class GetMKCV1DataCommand(Command[MKCData]):
    async def handle(self, db_wrapper, s3_wrapper):
        mkc_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "mkc.json")
        if mkc_bytes is None:
            raise Problem("MKCV1 data is not imported")
        return msgspec.json.decode(mkc_bytes, type=MKCData)

@dataclass
class GetXenforoUserDataCommand(Command[XFUser | None]):
    id: int

    async def handle(self, db_wrapper, s3_wrapper):
        xf_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "xf.json")
        if xf_bytes is None:
            raise Problem("MKC V1 data is not imported")
        xf_data = msgspec.json.decode(xf_bytes, type=XenforoData)

        for user in xf_data.xf_user:
            if user.user_id == self.id:
                return user

        return None

@dataclass
class ValidateXenforoPasswordCommand(Command[bool]):
    id: int
    password: str

    async def handle(self, db_wrapper, s3_wrapper):
        xf_bytes = await s3_wrapper.get_object(s3.MKCV1_BUCKET, "xf.json")
        if xf_bytes is None:
            raise Problem("MKC V1 data is not imported")
        xf_data = msgspec.json.decode(xf_bytes, type=XenforoData)

        for user_auth in xf_data.xf_user_authenticate:
            if user_auth.user_id == self.id:
                bcrypt_hash = user_auth.data[22:82] # data is in format 'a:1:{s:4:"hash",s:60:"$2y$...";}'
                return bcrypt.checkpw(self.password.encode('utf-8'), bcrypt_hash.encode('utf-8'))
        
        return False
