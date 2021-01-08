from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class Session(object):
    _instance = None
    FLAG = False

    def __init__(self, _DATABASE_URL):
        if not self.__class__.FLAG:
            self.engine = create_engine(
                _DATABASE_URL,
                echo=False,
                max_overflow=0,
                pool_size=20,
                pool_timeout=30,
                pool_recycle=3600
            )
            self.Session = sessionmaker(bind=self.engine)
            self.db = scoped_session(self.Session)
            self.__class__.FLAG = True

    def __getattr__(self, item):
        assert hasattr(self.db, item)
        return getattr(self.db, item)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
