from dataclasses import dataclass
from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, create_engine, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class InviteCodeModel(Base):
    __tablename__ = "invite_code"
    id = Column("id", Integer, primary_key=True)
    code = Column("code", String, unique=True, nullable=False)
    description = Column("description", String)
    created_at = Column("created_at", DateTime)


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


if __name__ == '__main__':
    persist = Persistent("test.sqlite")

    # persist.delete_code('14')
    print(persist.get_codes())
