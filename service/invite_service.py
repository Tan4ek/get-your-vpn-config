import json
import random
import string
import uuid
from dataclasses import dataclass
from typing import List, Optional

from retry import retry

from repository.openvpn_api import OpenvpnApi, BuildClient
from repository.persistant import Persistent, InviteCodeEntity, AlreadyExistCodeException
from repository.shadow_socks_api import ShadowSocksApi


@dataclass
class InviteCode:
    code: str
    description: str


@dataclass
class OpenvpnProviderClient:
    id: str
    invite_code: str
    ovpn_file: str


@dataclass
class ShadowSocks:
    id: str
    user_id: str
    port: int
    cipher: str
    secret: str


class OpenvpnProviderExistException(Exception):

    def __init__(self, invite_code: str):
        self.invite_code = invite_code


class ShadowSocksProviderExistException(Exception):

    def __init__(self, invite_code: str):
        self.invite_code = invite_code


def generate_invite_code(length: int = 8) -> str:
    return ''.join(random.SystemRandom().choices(string.ascii_uppercase + string.digits, k=length))


def generate_sssecret(length: int = 32) -> str:
    return ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=length))


class InviteService:

    def __init__(self, openvpn_api: OpenvpnApi, shadow_socks_api: ShadowSocksApi, persistent: Persistent):
        self._persistent = persistent
        self._shadow_socks_api = shadow_socks_api
        self._openvpn_api = openvpn_api

    @retry(AlreadyExistCodeException)  # retry until create uniq code
    def create_invite_code(self, description: str) -> InviteCode:
        code = generate_invite_code(length=10)
        code_entity = self._persistent.create_code(InviteCodeEntity(code, description))
        return InviteCode(code_entity.code, description)

    def delete_invite_code(self, code: str) -> bool:
        return self._persistent.delete_code(code)

    def get_code(self, code: str) -> Optional[InviteCode]:
        entity = self._persistent.get_code(code)
        if entity:
            return InviteCode(entity.code, entity.description)
        else:
            return None

    def get_codes(self) -> List[InviteCode]:
        return [InviteCode(entity.code, entity.description) for entity in self._persistent.get_codes()]

    def create_provider_openvpn(self, invite_code: str, password: str) -> Optional[OpenvpnProviderClient]:
        invite = self.get_code(invite_code)
        if invite:
            if self._persistent.exist_provider(invite.code, 'openvpn'):
                raise OpenvpnProviderExistException(invite.code)
            client_id = str(uuid.uuid4())
            openvpn_client = self._openvpn_api.create_client(BuildClient(client_id, password))

            payload = {
                'client_id': client_id,
                'ovpn_file': openvpn_client.ovpn_entity
            }
            provider_entity = self._persistent.create_provider(invite.code, 'openvpn', json.dumps(payload))
            return OpenvpnProviderClient(provider_entity.id, invite_code, openvpn_client.ovpn_entity)
        else:
            return None

    def exist_openvpn_provider(self, invite_code: str) -> bool:
        return self._persistent.exist_provider(invite_code, 'openvpn')

    def get_openvpn_providers(self, invite_code: str) -> List[OpenvpnProviderClient]:
        return [OpenvpnProviderClient(id=e.id, invite_code=e.invite_code, ovpn_file=json.loads(e.payload)['ovpn_file'])
                for e in self._persistent.get_providers(invite_code, 'openvpn')]

    def create_shadow_socks_provider(self, invite_code: str) -> Optional[ShadowSocks]:
        invite = self.get_code(invite_code)
        if invite:
            if self._persistent.exist_provider(invite.code, 'shadow_socks'):
                raise ShadowSocksProviderExistException(invite.code)

            user_id = f"{invite_code}_{str(uuid.uuid4())}"
            sssecret = generate_sssecret()
            created_user = self._shadow_socks_api.create_user(user_id, sssecret)

            payload = {
                'user_id': created_user.user_id,
                'port': created_user.port,
                'cipher': created_user.cipher,
                'secret': created_user.secret
            }
            provider_entity = self._persistent.create_provider(invite.code, 'shadow_socks', json.dumps(payload))
            return ShadowSocks(
                id=provider_entity.id,
                user_id=created_user.user_id,
                port=created_user.port,
                cipher=created_user.cipher,
                secret=created_user.secret
            )
        else:
            return None

    def get_shadow_socks_providers(self, invite_code: str) -> List[ShadowSocks]:
        providers = self._persistent.get_providers(invite_code, 'shadow_socks')

        shadow_socks = []
        for provider in providers:
            payload = json.loads(provider.payload)
            shadow_socks.append(ShadowSocks(
                id=provider.id,
                user_id=str(payload['user_id']),
                port=int(payload['port']),
                cipher=str(payload['cipher']),
                secret=str(payload['secret'])
            ))

        return shadow_socks


if __name__ == '__main__':
    persist = Persistent("test.sqlite")

    openvpn_api = OpenvpnApi('http://localhost:8090')
    admin_manager = InviteService(openvpn_api, persist)
    invite_code = admin_manager.create_invite_code()
    print(invite_code)
    print(InviteService.generate_random_code(10))
