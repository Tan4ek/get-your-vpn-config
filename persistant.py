from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine, delete, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class InviteCodeModel(Base):
    __tablename__ = "invite_code"
    id = Column("id", Integer, primary_key=True)
    code = Column("code", String, unique=True, nullable=False)
    description = Column("description", String)
    created_at = Column("created_at", DateTime, nullable=False)


class VpnProvider(Base):
    __tablename__ = "provider"
    id = Column("id", Integer, primary_key=True)
    type = Column("type", String, nullable=False)
    invite_code_id = Column("invite_code_id", Integer, ForeignKey("invite_code.id"), nullable=False)
    payload = Column("payload", JSON)
    created_at = Column("created_at", DateTime, nullable=False)


@dataclass
class InviteCodeEntity:
    code: str
    description: str


class AlreadyExistCode(ValueError):

    def __init__(self, code: str):
        self.code = code


class Persistent:

    def __init__(self, db_file_path: str):
        engine = create_engine(f"sqlite:///{db_file_path}")

        Session = sessionmaker()
        Session.configure(bind=engine)
        self._session = Session()
        Base.metadata.create_all(engine)

    def create_code(self, invite_code: InviteCodeEntity) -> InviteCodeEntity:
        try:
            self._session.add(InviteCodeModel(code=invite_code.code, created_at=datetime.utcnow(),
                                              description=invite_code.description))
            self._session.commit()
            return invite_code
        except IntegrityError as e:
            self._session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                raise AlreadyExistCode(invite_code.code)
            else:
                raise e

    def get_code(self, code: str) -> Optional[InviteCodeEntity]:
        model = self._session.query(InviteCodeModel).filter(InviteCodeModel.code == code).one_or_none()
        if model:
            return InviteCodeEntity(model.code, model.description)
        else:
            return None

    def delete_code(self, code: str) -> bool:
        try:
            result = self._session.execute(
                delete(InviteCodeModel).where(InviteCodeModel.code == code)
            )
            self._session.commit()
            return result.rowcount > 0
        except Exception as e:
            self._session.rollback()
            raise e

    def get_codes(self) -> List[InviteCodeEntity]:
        return [InviteCodeEntity(model.code, model.description) for model in
                (self._session.query(InviteCodeModel).order_by(InviteCodeModel.created_at).all())]

    def create_openvpn_provider(self, invite_code: str, payload: str):
        # payload - json
        invite_code_id = self._session.query(InviteCodeModel.id).filter(InviteCodeModel.code == invite_code).one()[0]
        self._session.add(VpnProvider(type='openvpn', invite_code_id=invite_code_id,
                                      payload=payload,
                                      created_at=datetime.utcnow()))
        self._session.commit()

    def exist_openvpn_provider(self, invite_code: str) -> bool:
        return self._session.query(InviteCodeModel).join(VpnProvider) \
                   .filter(InviteCodeModel.code == invite_code).count() > 0


if __name__ == '__main__':
    persist = Persistent("test.sqlite3")

    # persist.delete_code('14')
    print(persist.get_codes())

    print(persist.get_code('5QP4J2HIY1'))
    print(persist.create_openvpn_provider('5QP4J2HIY1', '{}'))
