import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Config


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Sqlite(metaclass=Singleton):
    base = declarative_base()

    def __init__(self, config: Config):
        self.log = logging.getLogger(__name__)
        self.session = None
        try:
            self.log.debug("Connecting to database: - %s", config.database.get_connection_string())
            self.engine = create_engine(config.database.get_connection_string())
            self.base.metadata.create_all(self.engine)
            self.session = sessionmaker(bind=self.engine)()
        except:
            self.log.error("Failed to connect to database", exc_info=True)
            raise
