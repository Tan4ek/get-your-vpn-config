import random
import string
from dataclasses import dataclass
from typing import List

from retry import retry

from persistant import Persistent, InviteCodeEntity, AlreadyExistCode


@dataclass
class InviteCode:
    code: str
    description: str


class AdminManager:

    def __init__(self, persistent: Persistent):
        self._persistent = persistent

    @retry(AlreadyExistCode)  # retry until create uniq code
    def create_invite_code(self, description: str) -> InviteCode:
        code = AdminManager.generate_random_code(length=10)
        code_entity = self._persistent.create_code(InviteCodeEntity(code, description))
        return InviteCode(code_entity.code, description)

    def delete_invite_code(self, code: str) -> bool:
        return self._persistent.delete_code(code)

    def get_codes(self) -> List[InviteCode]:
        return [InviteCode(entity.code, entity.description) for entity in self._persistent.get_codes()]

    @staticmethod
    def generate_random_code(length: int = 8) -> str:
        return ''.join(random.SystemRandom().choices(string.ascii_uppercase + string.digits, k=length))


if __name__ == '__main__':
    persist = Persistent("test.sqlite")

    admin_manager = AdminManager(persist)
    invite_code = admin_manager.create_invite_code()
    print(invite_code)
    print(AdminManager.generate_random_code(10))
