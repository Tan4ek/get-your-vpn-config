from dataclasses import dataclass

import requests


@dataclass
class BuildClient:
    name: str
    password: str


@dataclass
class ClientEntity:
    ovpn_entity: str


class CreateClientException(Exception):

    def __init__(self, name: str):
        self.name = name


class GetClientException(Exception):

    def __init__(self, name: str):
        self.name = name


class OpenvpnApi:

    def __init__(self, uri: str):
        self.__uri = uri

    def create_client(self, build_client: BuildClient) -> ClientEntity:
        try:
            response = requests.post(f"{self.__uri}/ovpn-config",
                                     params={'clientId': build_client.name, 'password': build_client.password})
            if response.status_code == 200:
                return ClientEntity(response.text)
            else:
                raise CreateClientException(build_client.name)
        except Exception:
            # todo exception logging
            raise CreateClientException(build_client.name)

    def get_client(self, name: str) -> ClientEntity:
        response = requests.get(f"{self.__uri}/ovpn-config",
                                params={'clientId': name})
        if response.status_code == 200:
            return ClientEntity(response.text)
        else:
            raise GetClientException(name)


if __name__ == '__main__':
    openvpn_api = OpenvpnApi('http://localhost:8090')
    e = openvpn_api.create_client(BuildClient('test102', 'kek1'))
    # e = openvpn_api.get_client('new_client1')
    print(e)
