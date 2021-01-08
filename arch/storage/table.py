from datetime import datetime

from sqlalchemy import Column, types, Integer, String, Text, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint

Base = declarative_base()


class Account(Base):
    __tablename__ = 'Account'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(128))
    username = Column('username', String(128), unique=True)
    password = Column('password', String(128))
    organization_id = Column('organization_id', Integer)
    role = Column('role', SmallInteger)
    cfg = Column('cfg', Text)
    """
        {
            "fate": {"ip": "", "port": "", "version": ""}
        }
    """

class DatasetFate(Base):
    __tablename__ = 'DatasetFate'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(128))
    user_id = Column('user_id', String(128))
    job_id = Column('job_id', String(128))
    name = Column('name', String(128), nullable=False, server_default="")


class WorkspaceFate(Base):
    __tablename__ = 'WorkspaceFate'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(128))
    name = Column('name', String(128), nullable=False, server_default="")
    creator = Column('creator', String(128), nullable=False, server_default="")
    description = Column('description', String(256), nullable=False, server_default="")


class AccountWorkspace(Base):
    __tablename__ = 'AccountWorkspace'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', String(128))
    workspace_uid = Column('workspace_uid', String(128))


class DatasetFateWorkspace(Base):
    __tablename__ = 'DatasetFateWorkspace'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    dataset_uid = Column('dataset_uid', String(128))
    workspace_uid = Column('workspace_uid', String(128))


if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine(
                "mysql+pymysql://root:111@192.168.89.155:3370/federated_learning?charset=utf8",
                echo=False,
                max_overflow=0,
                pool_size=20,
                pool_timeout=30,
                pool_recycle=3600
    )
    Base.metadata.create_all(engine)
