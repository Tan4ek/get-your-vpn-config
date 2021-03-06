import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

import alembic.config
from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine, delete, ForeignKey, Index
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class InviteCodeModel(Base):
    __tablename__ = "invite_codes"
    id = Column("id", Integer, primary_key=True)
    code = Column("code", String, unique=True, nullable=False)
    description = Column("description", String)
    created_at = Column("created_at", DateTime, nullable=False)


class VpnProviderModel(Base):
    __tablename__ = "providers"
    id = Column("id", String, primary_key=True)
    type = Column("type", String, nullable=False)
    invite_code_id = Column("invite_code_id", Integer, ForeignKey("invite_codes.id"), nullable=False)
    payload = Column("payload", JSON)
    external_id = Column("external_id", String, unique=True, index=True, nullable=False, default=str(uuid.uuid4()))
    created_at = Column("created_at", DateTime, nullable=False)


class TrafficRecordModel(Base):
    __tablename__ = "traffic_records"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    date_from = Column("date_from", Integer, nullable=False)
    date_to = Column("date_to", Integer, nullable=False)
    provider_id = Column("provider_id", String, ForeignKey("providers.id"), nullable=False)
    direction = Column("direction", String, nullable=False)
    quantity_bytes = Column("quantity_bytes", Integer, nullable=False)


Index("idx_from_to", TrafficRecordModel.date_from, TrafficRecordModel.date_to)


@dataclass
class InviteCodeEntity:
    code: str
    description: str


@dataclass
class VpnProviderEntity:
    id: str
    type: str
    invite_code: str
    payload: str


class TrafficDirection(Enum):
    IN = 1
    OUT = 2


@dataclass
class TrafficRecordEntity:
    id: int
    date_from: datetime
    date_to: datetime
    provider_id: str
    quantity_bytes: int
    direction: TrafficDirection


class AlreadyExistCodeException(Exception):

    def __init__(self, code: str):
        self.code = code


def __init_db__():
    alembic_args = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembic_args)


def timestamp_milliseconds(date_time: datetime) -> int:
    return int(date_time.replace(tzinfo=timezone.utc).timestamp() * 1000)


def datetime_from_milliseconds(milliseconds: int) -> datetime:
    return datetime.utcfromtimestamp(milliseconds / 1000)


class Persistent:

    def __init__(self, db_file_path: str):
        engine = create_engine(f"sqlite:///{db_file_path}")

        Session = sessionmaker()
        Session.configure(bind=engine)
        self._session = Session()
        __init_db__()

    def create_code(self, invite_code: InviteCodeEntity) -> InviteCodeEntity:
        try:
            self._session.add(InviteCodeModel(code=invite_code.code, created_at=datetime.utcnow(),
                                              description=invite_code.description))
            self._session.commit()
            return invite_code
        except IntegrityError as e:
            self._session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                raise AlreadyExistCodeException(invite_code.code)
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

    def create_provider(self, invite_code: str, external_id: str, provider_type: str,
                        payload: str) -> VpnProviderEntity:
        # payload - json
        provider_id = str(uuid.uuid4())
        invite_code_id = self._session.query(InviteCodeModel.id).filter(InviteCodeModel.code == invite_code).one()[0]
        self._session.add(VpnProviderModel(id=provider_id, type=provider_type, invite_code_id=invite_code_id,
                                           payload=payload,
                                           external_id=external_id,
                                           created_at=datetime.utcnow()))
        self._session.commit()
        return VpnProviderEntity(provider_id, provider_type, invite_code, payload)

    def get_providers(self, invite_code: str, provider_type: str):
        result = self._session.query(VpnProviderModel).join(InviteCodeModel) \
            .filter(InviteCodeModel.code == invite_code) \
            .filter(VpnProviderModel.type == provider_type) \
            .all()
        return [VpnProviderEntity(id=m.id, type=m.type, invite_code=invite_code, payload=m.payload) for m in result]

    def exist_provider(self, invite_code: str, provider_type: str):
        return self._session.query(InviteCodeModel).join(VpnProviderModel) \
                   .filter(InviteCodeModel.code == invite_code) \
                   .filter(VpnProviderModel.type == provider_type) \
                   .count() > 0

    def last_date_traffic_record(self, provider_type: str) -> Optional[datetime]:
        result = self._session.query(TrafficRecordModel).join(VpnProviderModel) \
            .filter(VpnProviderModel.type == provider_type) \
            .order_by(TrafficRecordModel.date_to.desc()) \
            .limit(1) \
            .all()
        if result:
            return datetime_from_milliseconds(result[0].date_to)
        else:
            return None

    def create_traffic_record(self, traffic_record: TrafficRecordEntity):
        self._session.add(TrafficRecordModel(date_from=timestamp_milliseconds(traffic_record.date_from),
                                             date_to=timestamp_milliseconds(traffic_record.date_to),
                                             provider_id=traffic_record.provider_id,
                                             direction=traffic_record.direction.name.lower(),
                                             quantity_bytes=traffic_record.quantity_bytes))
        self._session.commit()

    def provider_by_external_id(self, external_id: str) -> Optional[VpnProviderEntity]:
        result = self._session.query(VpnProviderModel, InviteCodeModel).join(InviteCodeModel) \
            .filter(VpnProviderModel.external_id == external_id).one_or_none()
        if result:
            return VpnProviderEntity(id=result[0].id, type=result[0].type, invite_code=result[1].code,
                                     payload=result[0].payload)
        else:
            return None
