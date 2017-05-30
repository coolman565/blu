import logging

from cement.core.controller import CementBaseController, expose
from cement.core.foundation import CementApp

from config import Config
from database import Sqlite
from handbrakeCLI.HandBrakeCLI import HandBrakeCLI
from makeMKV import MakeMKV
from metaData import Identify


class BluBaseController(CementBaseController):
    config = Config()
    config.load_config("config.yml")
    database = Sqlite(config)
    makemkv_cli = MakeMKV(config)
    identify = Identify(config)
    hanbrake_cli = HandBrakeCLI(config)

    class Meta:
        label = 'base'
        description = 'Blu The Ripper'
        arguments = [
        ]

    @expose(help="Rip content from disc", aliases=['r'])
    def rip(self):
        self.app.log.debug("Ripping")
        self.makemkv_cli.scan_discs()
        self.makemkv_cli.rip_all()
        self.identify.get_db_metadata()

    @expose(help="Compress ripped content", aliases=['c'])
    def compress(self):
        self.app.log.debug("Compressing")
        self.hanbrake_cli.compress_all()


class Blu(CementApp):
    class Meta:
        label = 'blu'
        base_controller = 'base'
        handlers = [BluBaseController]


with Blu() as app:
    app.run()

    exit(0)

    logging.basicConfig(level=logging.DEBUG)

    config = Config()
    config.load_config("config.yml")

    database = Sqlite(config)

    makemkv_cli = MakeMKV(config)
    identify = Identify(config)
    hanbrake_cli = HandBrakeCLI(config)

    # disc_details_list = makemkv_cli.scan_discs()

    # makemkv_cli.rip_all()

    # identify.get_db_metadata()

    hanbrake_cli.compress_all()
