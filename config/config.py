import logging
import yaml

from config import Database, Ripper, Identifier, Converter


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.database = Database()
        self.ripper = Ripper()
        self.identifier = Identifier()
        self.converter = Converter()

    def load_config(self, config_file):
        self.log.info("Reading from config file: %s", config_file)
        try:
            with open(config_file, 'r') as ymlFile:
                self.cfg = yaml.load(ymlFile)
                self.database.update(self.cfg['database'])
                self.ripper.update(self.cfg['ripper'])
                self.identifier.update(self.cfg['identifier'])
                self.converter.update(self.cfg['converter'])
        except:
            self.log.error("Failed to read from config file", exc_info=True)
