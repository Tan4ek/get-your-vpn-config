import json
import random
import string
import uuid
from dataclasses import dataclass
from typing import List

from retry import retry

from openvpn_api import OpenvpnApi, BuildClient
from persistant import Persistent, InviteCodeEntity, AlreadyExistCode


@dataclass
class InviteCode:
    code: str
    description: str


@dataclass
class OpenvpnProviderClient:
    ovpn_file: str


class AdminManager:

    def __init__(self, openvpn_api: OpenvpnApi, persistent: Persistent):
        self._persistent = persistent
        self._openvpn_api = openvpn_api

    @retry(AlreadyExistCode)  # retry until create uniq code
    def create_invite_code(self, description: str) -> InviteCode:
        code = AdminManager.generate_random_code(length=10)
        code_entity = self._persistent.create_code(InviteCodeEntity(code, description))
        return InviteCode(code_entity.code, description)

    def delete_invite_code(self, code: str) -> bool:
        return self._persistent.delete_code(code)

    def get_code(self, code: str) -> InviteCode:
        entity = self._persistent.get_code(code)
        return InviteCode(entity.code, entity.description)

    def get_codes(self) -> List[InviteCode]:
        return [InviteCode(entity.code, entity.description) for entity in self._persistent.get_codes()]

    def create_provider_openvpn(self, invite_code: str, password: str) -> OpenvpnProviderClient:
        invite = self.get_code(invite_code)
        if invite:
            client_id = str(uuid.uuid4())
            openvpn_client = self._openvpn_api.create_client(BuildClient(client_id, password))

            payload = {
                'client_id': client_id,
                'ovpn_file': openvpn_client.ovpn_entity
            }
            self._persistent.create_openvpn_provider(invite.code, json.dumps(payload))
            return OpenvpnProviderClient(openvpn_client.ovpn_entity)

    def exist_openvpn_provider(self, invite_code: str) -> bool:
        return self._persistent.exist_openvpn_provider(invite_code)

    @staticmethod
    def generate_random_code(length: int = 8) -> str:
        return ''.join(random.SystemRandom().choices(string.ascii_uppercase + string.digits, k=length))


if __name__ == '__main__':
    persist = Persistent("test.sqlite")

    openvpn_api = OpenvpnApi('http://localhost:8090')
    admin_manager = AdminManager(openvpn_api, persist)
    invite_code = admin_manager.create_invite_code()
    print(invite_code)
    print(AdminManager.generate_random_code(10))
