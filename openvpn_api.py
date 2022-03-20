from dataclasses import dataclass


@dataclass
class BuildClient:
    name: str
    password: str


@dataclass
class ClientEntity:
    ovpn_entity: str


class OpenvpnApi:

    def __init__(self, uri: str, secure_ca_password: str):
        self.__ur = uri
        self.__secure_ca_password = secure_ca_password

    def create_client(self, build_client: BuildClient) -> ClientEntity:
        # TODO implement http call
        return ClientEntity('')

    def get_client(self, name: str) -> ClientEntity:
        # TODO implement http call
        return ClientEntity('')
