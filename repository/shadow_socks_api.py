from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class ShadowSocksEntity:
    user_id: str
    port: int
    cipher: str
    secret: str


class CreateUserException(Exception):

    def __init__(self, message: str):
        self.message = message


class GetUserException(Exception):

    def __init__(self, message: str):
        self.message = message


# communication with https://github.com/Tan4ek/outline-ss-server-user-manager
class ShadowSocksApi:

    def __init__(self, uri: str):
        self.__uri = uri

    def create_user(self, user_id: str, sssecret: str) -> ShadowSocksEntity:
        response = requests.post(f"{self.__uri}/user",
                                 json={
                                     'user_id': user_id,
                                     'sssecret': sssecret
                                 })
        if response.status_code == 200:
            json_response = response.json()
            return ShadowSocksEntity(
                user_id=json_response['user_id'],
                port=json_response['port'],
                cipher=json_response['cipher'],
                secret=json_response['secret'],
            )
        else:
            raise CreateUserException(f"Can't create shadow socks user. Status: {response.status_code}, "
                                      f"text: {response.text}")

    def get_user(self, user_id: str) -> Optional[ShadowSocksEntity]:
        response = requests.get(f"{self.__uri}/user/{user_id}")

        if response.status_code == 200:
            json_response = response.json()
            return ShadowSocksEntity(
                user_id=json_response['user_id'],
                port=json_response['port'],
                cipher=json_response['cipher'],
                secret=json_response['secret'],
            )
        elif response.status_code == 404:
            return None
        else:
            raise GetUserException(f"Can't get shadow socks user by user_id '{user_id}'. "
                                   f"Status: {response.status_code}, text: {response.text}")
